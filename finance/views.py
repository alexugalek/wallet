import calendar
import datetime
import os
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.shortcuts import render
from .models import Categories, FinancialExpenses, AccountSettings, Bills
from django.urls import reverse
from .forms import ExpenseAddForm, AccountSettingsForm, SendEmailForm, AddBill, EditExpenseForm
from django.contrib.auth.models import User
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from wallet.settings import TODAY_IS, BASE_DIR, EMAIL_HOST_USER


def send_email_custom(subject, message, from_email, to_emails, attachment=None, tmp_attachments=True):
    email = EmailMessage(subject, message, from_email, to_emails)
    if attachment is not None:
        email.attach_file(attachment)
    email.send()
    if attachment and tmp_attachments:
        os.remove(attachment) if os.path.isfile(attachment) else None


def month_converter(month):
    months_dict = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    return months_dict.get(month)


def home(request):
    context = {
        'form': ExpenseAddForm()
    }
    template = 'home.html'
    return render(request, template, context)


class LoginRequiredCustomMixin(LoginRequiredMixin):
    pass
    # def dispatch(self, request, *args, **kwargs):
    #     if not request.user.is_authenticated:
    #         return redirect('login')
    #     return super().dispatch(request, *args, **kwargs)


SEND_EMAIL_MSG = None
ERROR_OCCURRED = False


class ExpenseAddView(LoginRequiredCustomMixin, CreateView):

    model = FinancialExpenses
    template_name = 'users/info.html'
    form_class = ExpenseAddForm

    def get_context_data(self, **kwargs):

        global SEND_EMAIL_MSG, ERROR_OCCURRED

        # identification of requested date
        now = datetime.datetime.utcnow()
        year, month, day = now.year, now.month, now.day
        year = self.kwargs.get('year_filter') or year
        month = month_converter(self.kwargs.get('month_filter')) or month

        # query to get all records for current month
        expenses_objects = FinancialExpenses.objects.filter(
            user__id=self.request.user.id, created__year=year,
            created__month=month).order_by('-created')

        # query to get all current categories
        categories_objects = Categories.objects.all().order_by('name')

        # query to get all bills
        bills_objects = Bills.objects.filter(user__id=self.request.user.id, created__year=year, created__month=month).values('created').annotate(value=Count('bill_photo'))

        # creation dict with next structure for daily report in each category:
        # coast_data = {current_date:
        #                            {category_1: coast_1},
        #                            .....................,
        #                            {category_n: coast_n}
        coast_data = {
            expense.created.date(): {
                category.name: 0 for category in categories_objects
            } for expense in expenses_objects
        }

        # update coast data to get access to bills if didn't any expenses add
        coast_data.update({
            bills['created']: {
                category.name: 0 for category in categories_objects
            } for bills in bills_objects
        })

        # creation dict for daily report with common coasts
        total_day_coast = {expense.created.date(): 0 for expense in expenses_objects}

        # creation dict for month report of coast in each category
        total_category_month_coast = {
            category.name: 0 for category in categories_objects
        }

        # total month coasts
        total_month_coast = 0

        # counting all expenses
        for day, categories in coast_data.items():
            for category, value in categories.items():
                day_category_fields = expenses_objects.filter(
                    subcategory__category__name=category, created__date=day)

                for field in day_category_fields:

                    coast = field.expense_value
                    coast_data[day][category] += coast
                    total_month_coast += coast
                    total_day_coast[day] += coast
                    total_category_month_coast[category] += coast

        # check account setting for update
        for category in categories_objects:
            if not AccountSettings.objects.filter(user__id=self.request.user.id,
                                                  category=category).exists():
                account = AccountSettings()
                account.user = self.request.user
                account.category = category
                account.save()

        if now.date().year == year and now.date().month == month:
            limit_values = {
                setting.category.name:
                setting.limit_value - coast_data.get(now.date(), {}).get(setting.category.name, 0) if setting.report else '-'
                for setting in AccountSettings.objects.filter(user__id=self.request.user.id).order_by('category__name')
            }

            settings_for_report = AccountSettings.objects.filter(user__id=self.request.user.id, report=True)

            total_day_limits = sum(setting.limit_value for setting in settings_for_report)

            total_day_coasts = sum(coast_data.get(now.date(), {}).get(setting.category.name, 0) for setting in settings_for_report)

            # check if there no any coasts
            total_day_coasts = 0 if not total_day_coasts else total_day_coasts.amount
            total_day_limits = 0 if not total_day_limits else total_day_limits.amount

            total_day_to_use = total_day_limits - total_day_coasts

            if total_day_coasts > total_day_limits:
                kwargs['balance_message'] = 'Overspending value'
            else:
                kwargs['balance_message'] = 'Balance to use today'
            kwargs['day_limits'] = total_day_to_use

        else:
            limit_values = None

        kwargs['categories_obj'] = categories_objects
        kwargs['coast_data'] = coast_data
        kwargs['total_day_coast'] = total_day_coast
        kwargs['total_month_coast'] = total_month_coast
        kwargs['total_category_month_coast'] = total_category_month_coast
        kwargs['current_year'] = year
        kwargs['current_month'] = calendar.month_name[month]
        kwargs['limits'] = limit_values
        kwargs['send_email_form'] = SendEmailForm({'pk': self.request.user.id, 'year': year, 'month': month})
        kwargs['add_bill_photo'] = AddBill()
        kwargs['bills'] = {count['created']: count['value'] for count in bills_objects}
        kwargs['send_email_msg'] = SEND_EMAIL_MSG
        kwargs['error_occurred'] = ERROR_OCCURRED

        SEND_EMAIL_MSG = None
        ERROR_OCCURRED = False

        return super().get_context_data(**kwargs)

    def get_success_url(self):
        success_url = self.request.POST.get('next', None)
        if success_url:
            return success_url
        return reverse('finance:info',
                       args=[self.request.user.id])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class DetailDayView(LoginRequiredCustomMixin, CreateView):
    model = FinancialExpenses
    template_name = 'users/detail.html'
    form_class = ExpenseAddForm

    def get_context_data(self, **kwargs):
        day_request = self.kwargs['date'][0:2]
        month_request = self.kwargs['date'][3:5]
        year_request = self.kwargs['date'][6::]
        detail_fields = FinancialExpenses.objects.filter(
            user__id=self.request.user.id, created__year=year_request,
            created__month=month_request, created__day=day_request
        )
        detail_bills = Bills.objects.filter(
            user__id=self.request.user.id, created__year=year_request,
            created__month=month_request, created__day=day_request
        )

        kwargs['detail_fields'] = detail_fields
        kwargs['detail_bills'] = detail_bills

        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'finance:detail', args=[self.request.user.id,
                                    self.kwargs['date']]
        )


class DetailUpdateView(LoginRequiredCustomMixin, UpdateView):
    model = FinancialExpenses
    template_name = 'users/detail.html'
    form_class = EditExpenseForm

    def get_context_data(self, **kwargs):
        kwargs['update_func'] = True
        kwargs['formatted_day'] = self.object.created.strftime("%d-%m-%Y")
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse(
            'finance:detail', args=[self.request.user.id,
                                    self.object.created.strftime("%d-%m-%Y")]
        )


class DeleteDataView(DeleteView):
    model = FinancialExpenses
    template_name = 'users/detail.html'

    def get_success_url(self):
        return reverse(
            'finance:detail', args=[self.request.user.id,
                                    self.object.created.strftime("%d-%m-%Y")]
        )


class SettingsCreateView(LoginRequiredCustomMixin, CreateView):

    model = AccountSettings
    template_name = 'users/account.html'
    form_class = ExpenseAddForm

    def get_context_data(self, **kwargs):
        all_settings = AccountSettings.objects.filter(
            user__id=self.kwargs['pk']
        )
        kwargs['all_settings'] = all_settings
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('finance:settings', args=[self.request.user.id])


class SettingsUpdateView(LoginRequiredCustomMixin, UpdateView):
    model = AccountSettings
    template_name = 'users/account.html'
    form_class = AccountSettingsForm

    def get_context_data(self, **kwargs):
        kwargs['update_func'] = True
        kwargs['category'] = self.object.category.name
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse('finance:settings', args=[self.request.user.id])

    def form_valid(self, form):
        record_queryset = AccountSettings.objects.filter(pk=self.object.pk).first()
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.category = record_queryset.category
        self.object.save()
        return super().form_valid(form)


@login_required
def send_email(request, pk):

    global SEND_EMAIL_MSG, ERROR_OCCURRED

    ERROR_OCCURRED = True

    if request.method == "POST":
        form = SendEmailForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user_email = User.objects.get(pk=pk).email
            info_data = []
            total_expenses = 0
            if user_email:
                subject = f'Expense statistics for {cd["year"]}-{calendar.month_name[cd["month"]]}'
                message = 'Find you statistic in attachment'
                file_to_send_url = f'{BASE_DIR}/finance/static/emails/{pk}-{cd["year"]}-{cd["month"]}.txt'

                for expense in FinancialExpenses.objects.filter(user__id=pk, created__year=cd["year"], created__month=cd["month"]):
                    info_data.append(f'{expense.created.strftime("%d-%m-%Y: %H:%M")} '
                                     f'was spent {expense.expense_value} '
                                     f'in {expense.subcategory.category.name}: {expense.subcategory.name}')
                    total_expenses += expense.expense_value
                info_data.append(f'Total expenses: {total_expenses}')

                try:
                    with open(file_to_send_url, 'w') as file:
                        file.write('\n'.join(info_data))

                    send_email_custom(subject, message, EMAIL_HOST_USER, [user_email, ], file_to_send_url)
                    SEND_EMAIL_MSG = 'Successful send on E-mail'
                    ERROR_OCCURRED = False
                except Exception as e:
                    print(e)
                    SEND_EMAIL_MSG = 'Something went wrong'
            return redirect('finance:info-detail',
                            pk=request.user.id,
                            year_filter=cd['year'],
                            month_filter=calendar.month_name[cd['month']])
        return HttpResponse('Bad query')
    return HttpResponse('Bad query')


def add_bill_photo(request, pk):

    redirect_url = request.POST.get('next', None)

    if request.method == "POST":
        add_bill_form = AddBill(data=request.POST,
                                files=request.FILES)
        files_list = request.FILES.getlist('bill_photo')
        if add_bill_form.is_valid():
            for file in files_list:
                Bills.objects.create(
                    user=User.objects.get(pk=pk),
                    bill_photo=file,
                )

    return redirect(redirect_url) if redirect_url else redirect('finance:info', pk=request.user.id)
