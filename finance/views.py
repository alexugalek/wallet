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
from wallet.settings import BASE_DIR, EMAIL_HOST_USER


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


SEND_EMAIL_MSG = None
ERROR_OCCURRED = False
FILES_ERROR = None
BAD_UPLOAD = None


def home(request):
    global FILES_ERROR, BAD_UPLOAD
    context = {
        'form': ExpenseAddForm(),
        'files_errors': FILES_ERROR,
        'bad_upload': BAD_UPLOAD,
    }
    template = 'home.html'
    FILES_ERROR = None
    BAD_UPLOAD = None
    return render(request, template, context)


class LoginRequiredCustomMixin(LoginRequiredMixin):
    pass


class ErrorFilesMessage(CreateView):

    def get_context_data(self, **kwargs):
        global FILES_ERROR, BAD_UPLOAD
        kwargs['files_errors'] = FILES_ERROR
        kwargs['bad_upload'] = BAD_UPLOAD
        FILES_ERROR = None
        BAD_UPLOAD = None
        return super().get_context_data(**kwargs)


class ExpenseAddView(LoginRequiredCustomMixin, ErrorFilesMessage):

    model = FinancialExpenses
    template_name = 'users/info.html'
    form_class = ExpenseAddForm

    def get_context_data(self, **kwargs):

        global SEND_EMAIL_MSG, ERROR_OCCURRED, FILES_ERROR, BAD_UPLOAD

        # identification of requested date
        now = datetime.datetime.utcnow()
        year, month, day = now.year, now.month, now.day
        year = self.kwargs.get('year_filter') or year
        month = month_converter(self.kwargs.get('month_filter')) or month

        # queryset to get all categories
        categories_objects = Categories.objects.all().order_by('name')

        # check account setting for update
        for category in categories_objects:
            if not AccountSettings.objects.filter(user__id=self.request.user.id,
                                                  category=category).exists():
                account = AccountSettings()
                account.user = self.request.user
                account.category = category
                account.save()

        # query to get all bills
        bills_objects = Bills.objects.filter(
            user__id=self.request.user.id, created__year=year,
            created__month=month).values('created').annotate(value=Count('bill_photo')
        )

        daily_expenses = {
            bills_object['created']: {0: 0} for bills_object in bills_objects
        }

        daily_expenses_queryset = FinancialExpenses.objects.filter(
            user__id=self.request.user.id,
            created__year=year,
            created__month=month,
        ).values('created__date', 'subcategory__category').annotate(value=Sum('expense_value'))

        daily_expenses.update({
            date['created__date']: {} for date in daily_expenses_queryset
        })

        for expense in daily_expenses_queryset:
            daily_expenses[expense['created__date']].update({
                expense['subcategory__category']: round(expense['value'], 2)
            })

        kwargs['daily_expenses'] = {
            key: daily_expenses[key] for key in reversed(sorted(daily_expenses))
        }

        total_daily_expenses = {
            date: sum(expenses.values()) or '-' for date, expenses in daily_expenses.items()
        }

        kwargs['total_daily_expenses'] = total_daily_expenses

        monthly_expenses_queryset = FinancialExpenses.objects.filter(
            user__id=self.request.user.id,
            created__year=year,
            created__month=month,
        ).values('subcategory__category').annotate(value=Sum('expense_value'))

        monthly_expenses = {
            expense['subcategory__category']: round(expense['value'], 2) for expense in monthly_expenses_queryset
        }

        kwargs['monthly_expenses'] = monthly_expenses

        total_monthly_expenses = sum(monthly_expenses.values())

        kwargs['total_monthly_expenses'] = total_monthly_expenses

        daily_expenses_included_in_report = FinancialExpenses.objects.filter(
            user__id=self.request.user.id,
            created__year=year,
            created__month=month,
            created__day=day,
            subcategory__category__accountsettings__report=True,
            subcategory__category__accountsettings__user__id=self.request.user.id,
        ).values('subcategory__category').annotate(value=Sum('expense_value'))

        daily_expenses_included_in_report = {
            expense['subcategory__category']: expense['value'] for expense in daily_expenses_included_in_report
        }

        kwargs['daily_expenses_included_in_report'] = daily_expenses_included_in_report

        limits_included_in_report = AccountSettings.objects.filter(
            user__id=self.request.user.id,
            report=True,
        ).values('category', 'limit_value')

        limits_included_in_report = {
            limit['category']: limit['limit_value'] - daily_expenses_included_in_report.get(limit['category'], 0)
            for limit in limits_included_in_report
        }

        kwargs['limits_included_in_report'] = limits_included_in_report

        daily_balance = sum(limits_included_in_report.values())

        kwargs['daily_balance'] = daily_balance

        if daily_balance < 0:
            kwargs['balance_message'] = 'Overspending value'
        else:
            kwargs['balance_message'] = 'Balance to use today'

        if now.date().year == year and now.date().month == month:
            limit_values = True
        else:
            limit_values = None

        kwargs['categories_obj'] = categories_objects
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

    def form_invalid(self, form):
        global BAD_UPLOAD

        super().form_invalid(form)

        BAD_UPLOAD = form.errors

        url_to_redirect = self.request.POST.get('next', None)
        if url_to_redirect:
            return redirect(url_to_redirect)
        return redirect('finance:info', pk=self.request.user.id)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return super().form_valid(form)


class DetailDayView(LoginRequiredCustomMixin, ErrorFilesMessage):
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
        for bill in detail_bills:
            if not os.path.isfile(f'{BASE_DIR}{bill.bill_photo.url}'):
                Bills.objects.filter(id=bill.id).delete()

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
        global FILES_ERROR
        kwargs['update_func'] = True
        kwargs['formatted_day'] = self.object.created.strftime("%d-%m-%Y")
        kwargs['files_errors'] = FILES_ERROR
        FILES_ERROR = None
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

                for expense in FinancialExpenses.objects.filter(user__id=pk, created__year=cd["year"], created__month=cd["month"]).select_related('subcategory'):
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
    global FILES_ERROR

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
            FILES_ERROR = None
        else:
            FILES_ERROR = add_bill_form.errors

    return redirect(redirect_url) if redirect_url else redirect('finance:info', pk=request.user.id)
