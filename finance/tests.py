import datetime
from unittest import mock
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
import ddt
from wallet.settings import MEDIA_ROOT
from .forms import ExpenseAddForm, AddBill
from djmoney.money import Money
from .models import Categories, AccountSettings, SubCategories, \
    FinancialExpenses, TelegramCredentials
from django.db.utils import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile
from .management.commands.bot import get_message


# Create your tests here.


class HomeTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_home_response_status_code_200(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


class CategoryTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.category = Categories.objects.create(
            name='newcategory'
        )

    def test_category_exists(self):
        self.assertTrue(
            Categories.objects.filter(name=self.category.name).exists()
        )

    def test_category_unique_name_exception(self):
        with self.assertRaises(Exception) as raised:
            Categories.objects.create(name='newcategory')
        self.assertEqual(IntegrityError, type(raised.exception))


class SubCategoryTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.category = Categories.objects.create(
            name='newcategory'
        )
        self.subcategory = SubCategories.objects.create(
            name='subcategory',
            category=self.category,
        )

    def test_subcategory_exists(self):
        self.assertTrue(
            SubCategories.objects.filter(category=self.category).exists()
        )


class ExpenseAddViewTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.request_factory = RequestFactory()
        self.user = User.objects.create_user(
            username='username',
            password='password',
            email='email',
        )
        self.client.login(username='username', password='password')

    # self.category1 = Categories.objects.create(name='test_name_1')
    # self.category2 = Categories.objects.create(name='test_name_2')

    def test_expense_add_view_response_status_code_200(self):
        response = self.client.get('/finance/info/1/')
        self.assertEqual(response.status_code, 200)

    def test_expense_add_view_with_date_response_status_code_200(self):
        response = self.client.get('/finance/info/1/2020-April?')
        self.assertEqual(response.status_code, 200)


@ddt.ddt
class ExpenseAddFormTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            password='password',
            email='email',
        )
        self.client.login(username='username', password='password')
        self.category = Categories.objects.create(name='category')
        self.subcategory = SubCategories.objects.create(
            name='subcategory',
            category=self.category,
        )

    def test_add_expense_form(self):
        response = self.client.post(
            '/finance/info/1/',
            {
                'expense_value_0': 25,
                'expense_value_1': 'USD',
                'subcategory': self.subcategory.pk,
            }
        )

        self.assertRedirects(response, '/finance/info/1/')
        self.assertTrue(
            FinancialExpenses.objects.filter(
                user=self.user,
                expense_value=Money(25, 'USD'),
                subcategory=self.subcategory,
            )
        )

    @ddt.data(
        (2, 'USD', 1, True),
        (None, 'USD', 1, False),
        (2, None, 1, False),
        (2, 'USD', None, False),
    )
    @ddt.unpack
    def test_add_expense_form_validation(self, value, currency, subcategory, result):
        form_data = {
            'expense_value_0': value,
            'expense_value_1': currency,
            'subcategory': subcategory,
        }
        form = ExpenseAddForm(data=form_data)
        self.assertEqual(form.is_valid(), result)


@ddt.ddt
class DetailEditViewTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            password='password',
            email='email',
        )
        self.client.login(username='username', password='password')
        self.category = Categories.objects.create(name='category1')
        self.subcategory = SubCategories.objects.create(
            name='subcategory1',
            category=self.category,
        )
        self.expense_first = FinancialExpenses.objects.create(
            user=self.user,
            expense_value=Money(1.10, 'USD'),
            subcategory=self.subcategory
        )
        self.expense_second = FinancialExpenses.objects.create(
            user=self.user,
            expense_value=Money(2.20, 'USD'),
            subcategory=self.subcategory
        )

    def test_detail_view_response_status_code_200(self):
        response = self.client.get('/finance/info/1/detail/12-05-2020/')
        self.assertEqual(response.status_code, 200)

    def test_detail_view_context_data(self):
        now = datetime.datetime.utcnow().strftime("%d-%m-%Y")
        response = self.client.get('/finance/info/1/detail/{}/'.format(now))
        queryset_in_context_data = response.context_data['view'].get_context_data()['detail_fields']
        self_queryset = FinancialExpenses.objects.filter(user=self.user)
        for number, queryset in enumerate(self_queryset):
            self.assertEqual(
                queryset.expense_value,	queryset_in_context_data[number].expense_value
            )

    @ddt.data(
        (1, 200, ),
        (2, 200, ),
        (3, 404, ),
    )
    @ddt.unpack
    def test_update_view_response_status(self, pk, status_code_result):
        response = self.client.get('/finance/info/1/update/{}/'.format(pk))
        self.assertEqual(response.status_code, status_code_result)

    @ddt.data(
        (25, 1, ),
        (15, 2, ),
    )
    @ddt.unpack
    def test_update_info(self, value, id):
        self.client.post(
            '/finance/info/1/update/{}/'.format(id),
            {
                'expense_value_0': value,
                'expense_value_1': 'USD',
                'subcategory': self.subcategory.pk,
                'created': datetime.datetime.utcnow(),
            }
        )
        self.assertEqual(FinancialExpenses.objects.get(pk=id).expense_value, Money(value, 'USD'))

    def test_delete_expense(self):
        self.client.post(
            '/finance/info/1/delete/1/'
        )
        self.assertFalse(FinancialExpenses.objects.filter(pk=1).exists())
        self.assertTrue(FinancialExpenses.objects.filter(pk=2).exists())


@ddt.ddt
class AccountSettingsTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            password='password',
        )
        self.client.login(username='username', password='password')
        self.category_1 = Categories.objects.create(name='category_1')
        self.category_2 = Categories.objects.create(name='category_2')
        self.client.get('/finance/info/1/')

    @ddt.data('category_1', 'category_2')
    def test_account_settings_creation_on_info_url(self, category):
        self.assertTrue(AccountSettings.objects.filter(
            user=self.user, category__name=category).exists()
                        )

    @ddt.data('category_1', 'category_2')
    def test_account_settings_creation_on_registration_url(self, category):
        self.client.logout()
        self.client.post(
            '/registration/',
            {
                'username': 'username123',
                'password': 'password',
                'password2': 'password',
                'email': 'email@mail.ru',
            }
        )
        self.assertTrue(AccountSettings.objects.filter(
            user__username='username123', category__name=category).exists()
                        )

    def test_account_settings_quantity_creation_on_info_url(self):
        self.assertEqual(len(AccountSettings.objects.filter(user=self.user)), 2)

    @ddt.data(
        (1, 200, ),
        (2, 200, ),
        (3, 404, ),
    )
    @ddt.unpack
    def test_edit_settings_response_status_code(self, pk, status_code_result):
        response = self.client.get('/finance/info/settings/1/{}/'.format(pk))
        self.assertEqual(response.status_code, status_code_result)

    @ddt.data(
        (2, 100, True),
        (1, 50, True),
        (1, 100, False),
    )
    @ddt.unpack
    def test_edit_settings(self, category_id, limit_value, report):
        self.client.post(
            '/finance/info/settings/1/{}/'.format(category_id),
            {
                'category': category_id,
                'limit_value_0': limit_value,
                'limit_value_1': 'USD',
                'report': report,
            }
        )
        self.assertTrue(
            AccountSettings.objects.filter(
                category__id=category_id,
                limit_value=Money(limit_value, 'USD'),
                report=report
            )
        )




class AddBillTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            password='password',
        )
        self.client.login(username='username',password='password')
        self.bill_photo = SimpleUploadedFile(
            name='test_img.jpg', content=open(
                '{}/files-for-tests/example-less-10-Mb.jpg'.format(
                    MEDIA_ROOT), 'rb').read(), content_type="image/jpg"
        )

    def test_add_bill_photo_successful(self):

        with mock.patch('finance.views.Bills.objects.create') as add_bill_mock:

            self.client.post(
                '/finance/add-bill/1/',
                {
                    'bill_photo': self.bill_photo,
                }
            )

            self.assertTrue(
                add_bill_mock.call_args_list[0][1]['bill_photo'].name, 'test_img.jpeg')
#
#
    def test_add_bill_photo_large_size_unsuccessful(self):

        bill_photo = SimpleUploadedFile(
            name='test_img.jpg', content=open(
                '{}/files-for-tests/example-more-10-Mb.jpg'.format(MEDIA_ROOT),
                'rb').read(), content_type="image/jpg"
        )

        form_data = {
            'bill_photo': bill_photo,
        }

        form = AddBill(data=form_data)

        self.assertFalse(form.is_valid())

    def test_add_bill_photo_redirect(self):

        with mock.patch('finance.views.Bills.objects.create') as add_bill_mock:

            response = self.client.post(
                '/finance/add-bill/1/',
                {
                    'bill_photo': self.bill_photo,
                }
            )

            self.assertRedirects(response, '/finance/info/1/')

    def test_add_bill_photo_login_required(self):

        with mock.patch('finance.views.Bills.objects.create') as add_bill_mock:
            self.client.logout()
            response = self.client.post(
                '/finance/add-bill/1/',
                {
                    'bill_photo': self.bill_photo,
                }
            )

            self.assertRedirects(response, '/accounts/login/?next=/finance/add-bill/1/')


class SendStatisticOnEmail(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            password='password',
            email='email@mail.com'
        )
        self.client.login(username='username',password='password')

    def test_statistic_email_send(self):

        with mock.patch('finance.views.open'), mock.patch('finance.views.send_email_custom') as mail_mock:
            self.client.post(
                '/finance/send-email/1/',
                {
                    'pk': 1,
                    'year': 2020,
                    'month': 5,
                }
            )
            self.assertEqual(mail_mock.call_args_list[0][0][3][0], "email@mail.com")
            self.assertIn('1-2020-5.txt', mail_mock.call_args_list[0][0][4])

    def test_redirect_to_login(self):
        self.client.logout()
        response = self.client.post(
            '/finance/send-email/1/',
            {
                'pk': 1,
                'year': 2020,
                'month': 5,
            }
        )
        self.assertRedirects(response, '/accounts/login/?next=/finance/send-email/1/')

    def test_statistic_email_send_once(self):
        with mock.patch('finance.views.open'), mock.patch('finance.views.EmailMessage.attach_file'), mock.patch('finance.views.EmailMessage.send') as mail_mock:

            self.client.post(
                '/finance/send-email/1/',
                {
                    'pk': 1,
                    'year': 2020,
                    'month': 5,
                }
            )
            self.assertEqual(mail_mock.call_count, 1)

@ddt.ddt
class MessageHandlerTelegramBorTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='username',
            password='password'
        )
        TelegramCredentials.objects.create(
            user=self.user,
            telegram_id=1,
        )

    @ddt.data(*SubCategories.objects.all().select_related('category'))
    def test_create_expense_via_msg(self, subcategory):
        Categories.objects.create(
            name=subcategory.category.name,
        )
        SubCategories.objects.create(
            name=subcategory.name,
            category=Categories.objects.first()
        )
        text = subcategory.name + ' 20'

        result = get_message(text, 1)
        if subcategory.name != 'Other':

            self.assertTrue(FinancialExpenses.objects.filter(subcategory__name=subcategory.name).exists())
            self.assertIn('was successful added to {}'.format(subcategory.name), result)

    @ddt.data(*SubCategories.objects.all().select_related('category'))
    def test_not_create_expense_via_msg_with_zero_value(self, subcategory):
        Categories.objects.create(
            name=subcategory.category.name,
        )
        SubCategories.objects.create(
            name=subcategory.name,
            category=Categories.objects.first()
        )
        text = subcategory.name + ' 0'

        result = get_message(text, 1)

        if subcategory.name != 'Other':
            self.assertFalse(FinancialExpenses.objects.filter(subcategory__name=subcategory.name).exists())
            self.assertIn("We don't accept 0 value", result)

    @ddt.data(*SubCategories.objects.all().select_related('category'))
    def test_balance_msg_with_report(self, subcategory):
        Categories.objects.create(name=subcategory.category.name)
        SubCategories.objects.create(name=subcategory.name, category=Categories.objects.first())
        FinancialExpenses.objects.create(
            user=self.user,
            expense_value=Money(10, 'USD'),
            subcategory=SubCategories.objects.first()
        )
        AccountSettings.objects.create(
            user=self.user,
            category=Categories.objects.first()
        )
        result = get_message('balance', 1)
        self.assertIn('Your balance for today is still : 90', result)
        self.assertIn('Your spent today : 10', result)

    @ddt.data(*SubCategories.objects.all().select_related('category'))
    def test_balance_msg_without_report(self, subcategory):
        Categories.objects.create(name=subcategory.category.name)
        SubCategories.objects.create(name=subcategory.name,
                                     category=Categories.objects.first())
        FinancialExpenses.objects.create(
            user=self.user,
            expense_value=Money(20, 'USD'),
            subcategory=SubCategories.objects.first()
        )
        AccountSettings.objects.create(
            user=self.user,
            category=Categories.objects.first(),
            report=False
        )
        result = get_message('balance', 1)
        self.assertNotIn('Your balance for today is still', result)
        self.assertIn('Your spent today : 20', result)

    def test_msg_for_invalid_data(self):
        result = get_message('something', 1)
        self.assertIn('If you want to add some expenses use next format', result)
