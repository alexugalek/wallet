from django.core import mail
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .forms import AuthUserForm, RegistrationLoginForm, EditInfo
import ddt

# Create your tests here.


@ddt.ddt
class AuthenticateTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            password='password',
        )

    def test_user_login_successful(self):
        logged_in = self.client.login(username='username', password='password')
        self.assertEqual(logged_in, True)

    @ddt.data(
        ('bad_username', 'password', ),
        ('username', 'bad_password', ),
    )
    @ddt.unpack
    def test_user_login_bad_credentials(self, username, password):
        logged_in = self.client.login(username=username, password=password)
        self.assertEqual(logged_in, False)

    def test_login_return_status_code_302(self):
        response = self.client.post(
            '/accounts/login/',
            {
                'username': 'username',
                'password': 'password',
            }
        )
        self.assertEqual(response.status_code, 302)

    def test_login_return_status_code_200(self):
        response = self.client.post(
            '/accounts/login/',
            {
                'username': 'username',
                'password': 'bad_password',
            }
        )
        self.assertEqual(response.status_code, 200)

    @ddt.data(
        ('username', 'password', True),
        ('bad_username', 'password', False, '__all__', 'Please enter a correct username and password. Note that both fields may be case-sensitive.'),
        ('username', 'bad_password', False, '__all__', 'Please enter a correct username and password. Note that both fields may be case-sensitive.'),
        ('', 'password', False, 'username', 'This field is required.'),
        ('username', '', False, 'password', 'This field is required.'),
    )
    @ddt.unpack
    def test_login_form_valid(self, username, password, result, error_key=None, error_msg=None):
        form_data = {
            'username': username,
            'password': password,
        }
        form = AuthUserForm(data=form_data)
        self.assertEqual(form.is_valid(), result)
        if error_key is not None and error_msg is not None:
            self.assertEqual(form.errors.get(error_key)[0], error_msg)


@ddt.ddt
class AuthorizationTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            password='password',
        )

    @ddt.data(
        ('/finance/info/1/', 'username', 200, ),
        ('/finance/info/1/', 'bad_username', 302, ),
        ('/finance/info/1/2020-April?/', 'username', 200, ),
        ('/finance/info/1/2020-April?/', 'bad_username', 302, ),
        ('/finance/info/1/detail/07-05-2021/', 'username', 200, ),
        ('/finance/info/1/detail/07-05-2021/', 'bad_username', 302,),
        ('/finance/info/settings/1/', 'username', 200, ),
        ('/finance/info/settings/1/', 'bad_username', 302, ),
        ('/edit/', 'username', 200, ),
        ('/edit/', 'bad_username', 302, ),
    )
    @ddt.unpack
    def test_urls_login_required(self, url, username, response_status_code):
        self.client.post(
            '/accounts/login/',
            {
                'username': username,
                'password': 'password',
            }
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, response_status_code)


@ddt.ddt
class RegistrationTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_registration_user(self):
        response = self.client.post(
            '/registration/',
            {
                'username': 'username',
                'password': 'password',
                'password2': 'password',
                'email': 'email@mail.ru',
            }
        )
        user = User.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(user.username, 'username')
        self.assertEqual(user.email, 'email@mail.ru')

    @ddt.data(
        ('username1', True, ),
        ('username', False, 'A user with that username already exists.', ),
    )
    @ddt.unpack
    def test_unique_username(self, username, result, error_msg=None):
        self.client.post(
            '/registration/',
            {
                'username': 'username',
                'password': 'password',
                'password2': 'password',
                'email': 'email@mail.ru',
            }
        )

        form_data = {
            'username': username,
            'password': 'password',
            'password2': 'password',
            'email': 'email@mail.ru',
        }
        form = RegistrationLoginForm(data=form_data)
        self.assertEqual(form.is_valid(), result)
        if error_msg is not None:
            self.assertEqual(form.errors.get('username')[0], error_msg)

    @ddt.data(
        ('username', 'password', 'password', 'email@mail.com', True),
        ('', 'password', 'password', 'email@mail.com', False, 'username', 'This field is required.'),
        ('usernameя', 'password', 'password', 'email@mail.com', False, 'username', 'Your username should contains only latin symbols, numbers and underscore'),
        ('username', '', '', 'email@mail.com', False, 'password', 'This field is required.'),
        ('username', '', '', 'email@mail.com', False, 'password2', 'This field is required.'),
        ('username', 'pas', 'pas', 'email@mail.com', False, 'password2', 'Please enter password with more than 4 symbols'),
        ('username', 'password1', 'password2', 'email@mail.com', False, 'password2', 'Passwords mismatch'),
        ('username', 'password', 'password', 'email.mail.com', False, 'email', 'Enter a valid email address.'),
    )
    @ddt.unpack
    def test_registration_form_valid(self, username, password, password2, email, result, error_key=None, error_msg=None):

        form_data = {
            'username': username,
            'password': password,
            'password2': password2,
            'email': email,
        }
        form = RegistrationLoginForm(data=form_data)
        self.assertEqual(form.is_valid(), result)
        if error_key is not None and error_msg is not None:
            self.assertEqual(form.errors.get(error_key)[0], error_msg)


class PasswordResetTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.email = 'email@mail.com'
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            password='password',
            email=self.email,
        )

    def test_forgotten_password_response_status_code_200(self):
        response = self.client.get('/password_reset/')
        self.assertEqual(response.status_code, 200)

    def test_reset_password_redirection(self):
        self.response = self.client.post(
            '/password_reset/',
            {
                'email': self.email,
            }
        )
        self.assertRedirects(self.response, '/password_reset/done/')

    def test_send_password_reset_email(self):
        self.client.post(
            '/password_reset/',
            {
                'email': self.email,
            }
        )
        self.assertEqual(1, len(mail.outbox))

    def test_password_reset_done_response_status_code_200(self):
        response = self.client.get('/password_reset/done/')
        self.assertEqual(response.status_code, 200)

    def test_password_reset_confirm_response_status_code_200(self):
        self.client.post(
            '/password_reset/',
            {
                'email': self.email,
            }
        )
        uid = mail.outbox[0].body.splitlines()[1].split('/')[4]
        token = mail.outbox[0].body.splitlines()[1].split('/')[5]

        response = self.client.get('/reset/{}/{}'.format(uid, token), follow=True)
        self.assertEqual(response.status_code, 200)


@ddt.ddt
class EditInfoTestCase(TestCase):

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = User.objects.create_user(
            username='username',
            password='password',
            email='email@mail.com',
        )
        self.client.login(
            username='username',
            password='password',
        )

    def test_edit_info_response_status_code_200(self):
        response = self.client.get('/edit/')
        self.assertEqual(response.status_code, 200)

    def test_edit_info_response_status_code_302(self):
        self.client.logout()
        response = self.client.get('/edit/')
        self.assertEqual(response.status_code, 302)

    def test_edit_info_redirect_to_login(self):
        self.client.logout()
        response = self.client.get('/edit/')
        self.assertRedirects(response, '/accounts/login/?next=/edit/')

    def test_edit_username_info(self):
        self.client.post(
            '/edit/',
            {
                'username': 'newusername',
                'email': 'email@mail.com',
            }
        )
        self.assertEqual(User.objects.first().username, 'newusername')

    def test_edit_email_info(self):
        self.client.post(
            '/edit/',
            {
                'username': 'username',
                'email': 'newemail@mail.com',
            }
        )
        self.assertEqual(User.objects.first().email, 'newemail@mail.com')

    @ddt.data(
        ('newusername', 'newemail@mail.com', True),
        ('newuser name', 'newemail@mail.com', False),
        ('newusernameя', 'newemail@mail.com', False),
        ('', 'newemail@mail.com', False),
        ('newusername', '', True),
        ('newusername', 'newemailmail.com', False),
    )
    @ddt.unpack
    def test_edit_info_form_is_valid_status(self, username, email, result):
        form_data = {
                'username': username,
                'email': email,
            }
        form = EditInfo(data=form_data)

        self.assertEqual(form.is_valid(), result)
