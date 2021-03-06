from django.core import mail
from django.forms import Field
from django.test import TestCase, Client
from django.contrib.auth import get_user
from django.urls import reverse

from account.forms import MyLoginView
from .models import User


class LoginViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="fake_user",
                                        email='fake_mail@email.com')
        self.user.set_password('fake_password')
        self.user.save()
        self.client = Client()
        self.good_authentication_data = {'username': 'fake_user',
                                         'password': 'fake_password'}
        self.bad_authentication_data = {'username': 'bad_user',
                                        'password': 'bad_password'}

    def test_login_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_form_is_valid_with_good_authentication_data(self):
        """Test if login form with good authentication data is valid"""
        loginForm = MyLoginView.authentication_form(None,
                                                    self.good_authentication_data)
        required_error = [str(Field.default_error_messages['required'])]
        self.assertTrue(loginForm.is_valid())
        self.assertNotEqual(loginForm['password'].errors, required_error)

    def test_login_form_is_not_valid_with_failed_data(self):
        """Test if login form with failed data is invalide"""
        loginForm = MyLoginView.authentication_form(None,
                                                    {'username': 'fake_user'})
        required_error = [str(Field.default_error_messages['required'])]
        self.assertFalse(loginForm.is_valid())
        self.assertEqual(loginForm['password'].errors, required_error)
        loginForm = MyLoginView.authentication_form(None, {
            'password': 'fake_password'})
        self.assertFalse(loginForm.is_valid())
        self.assertEqual(loginForm['username'].errors, required_error)

    def test_login_page_posted_with_good_authentication_data(self):
        """ If user data are good, then is the user is authenticate and redirect to index page """
        response = self.client.post('/', self.good_authentication_data)
        # Test if user is authenticate
        user = get_user(self.client)
        self.assertTrue(user.is_authenticated)
        # Test if page redirection
        self.assertEqual(response.status_code, 302)

    def test_login_page_posted_with_bad_user_data(self):
        """ If user data are bad, user is not authenticate and refresh the login page """
        response = self.client.post('/', self.bad_authentication_data)
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
        self.assertEqual(response.status_code, 200)


class LogoutViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="fake_user",
                                        email='fake_mail@email.com')
        self.user.set_password('fake_password')
        self.user.save()

    def test_logout_page(self):
        client = Client()
        client.force_login(self.user)
        # Test if user is logged in after login
        user = get_user(client)
        self.assertFalse(user.is_anonymous)
        # Call logout page
        response = client.get(reverse('account:logout'))
        # Test if user is unlogged after call logout page
        user = get_user(client)
        self.assertTrue(user.is_anonymous)
        # Test if redirect after call logout page
        self.assertEqual(response.status_code, 302)


class PassWordResetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="fake_user",
                                        email='fake_mail@email.com')
        self.user.set_password('fake_password')
        self.user.save()
        self.client = Client()
        self.new_password = "new_fake_password"

    def test_password_reset_page(self):
        response = self.client.get(reverse('account:password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0],
                         'account/password_reset.html')

        # Post the response with user "email address"
        response = self.client.post(reverse('account:password_reset'),
                                    {'email': 'fake_mail@email.com'})
        self.assertEqual(response.status_code, 302)

        # Check if email is send with subject
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject,
                         'Réinitialisation du mot de passe HomeCenter.')
        # Create user id and token
        uid = response.context[0]['uid']
        token = response.context[0]['token']
        return uid, token

    def test_password_reset_done_page(self):
        response = self.client.get(reverse('account:password_reset_done'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0],
                         'account/password_reset_done.html')

    def test_password_reset_confirm_page_with_uid_and_token_to_get_password_change_form(
            self):
        self.uid, self.token = self.test_password_reset_page()
        response = self.client.get(reverse('account:password_reset_confirm',
                                           kwargs={'uidb64': self.uid,
                                                   'token': self.token}),
                                   follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0],
                         'account/password_reset_confirm.html')

    def test_password_reset_confirm_page_with_new_password(self):
        # Check if old password is in database
        user = User.objects.get(username='fake_user')
        self.assertEqual(user.check_password('fake_password'), True)
        # Get password change page
        self.test_password_reset_confirm_page_with_uid_and_token_to_get_password_change_form()
        # Post password change page with new password
        response = self.client.post(reverse('account:password_reset_confirm',
                                            kwargs={'uidb64': self.uid,
                                                    'token': "set-password"}),
                                    {'new_password1': self.new_password,
                                     'new_password2': self.new_password},
                                    follow=True)
        # Check the reponse page
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0],
                         'account/password_reset_complete.html')
        # Check if new password has been set in database
        user = User.objects.get(username='fake_user')
        self.assertEqual(user.check_password(self.new_password), True)

    def test_password_reset_complete_page(self):
        response = self.client.get(reverse('account:password_reset_complete'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name[0],
                         'account/password_reset_complete.html')


class UserAdminTestCase(TestCase):
    def setUp(self):
        # Create superuser
        self.user_admin = User.objects.create_superuser(username="fake_admin",
                                                        email='fake_admin_mail@email.com')
        self.user_admin.set_password('fake_admin_password')
        self.user_admin.save()
        # Create simple user
        self.user = User.objects.create(username="fake_user",
                                        email='fake_mail@email.com')
        self.user.set_password('fake_password')
        self.user.save()
        # Instance Client()
        self.client = Client()
        # Ajax json data
        self.Ajax_post_jsonData = {
            'user_id': self.user.id,
            'action': 'UserDelete'
        }
        self.Ajax_post_success = {'action': 'UserDelete',
                                  'messages': {
                                      'success': "L'utilisateur à été "
                                                 "supprimé avec succès !"}}

    def test_display_users_administration_view(self):
        # Test display page if not logged
        response = self.client.get(reverse('account:user_admin'))
        self.assertEqual(response.status_code, 302)
        # Test with superuser logged
        self.client.force_login(self.user_admin)
        response = self.client.get(reverse('account:user_admin'))
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        # Superuser must be logged
        self.client.force_login(self.user_admin)
        # Test Ajax post delete user with succes
        response = self.client.post(reverse('account:user_admin'),
                                    {'user_id': self.user.id,
                                     'action': 'UserDelete'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.Ajax_post_success, response.json())
        # Test Ajax post delete user with error
        response = self.client.post(reverse('account:user_admin'),
                                    {'user_id': self.user.id + 1,
                                     'action': 'UserDelete'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(
            {'messages': {
                'error': "L'utilisateur n'a pas été supprimé ! Erreur: User "
                         "matching query does not exist."},
             'action': 'UserDelete'},
            response.json())
        self.assertEqual(response.status_code, 200)
