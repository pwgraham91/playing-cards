from django.core import mail
from django.core.exceptions import ValidationError
from django.forms import EmailField
from cards.forms import EmailUserCreationForm
from cards.models import Player

__author__ = 'GoldenGate'
from django.test import TestCase


# testing email forms
class FormTestCase(TestCase):
    def test_clean_username_exception(self):
        # Create a player so that this username we're testing is already taken
        Player.objects.create_user(username='test-user')

        # set up the form for testing
        form = EmailUserCreationForm()
        form.cleaned_data = {'username': 'test-user'}
        with self.assertRaises(ValidationError):
            form.clean_username()

    def test_clean_username(self):
        form = EmailUserCreationForm()
        form.cleaned_data = {
            'username': 'test-user'
        }
        self.assertTrue(form.clean_username() == 'test-user')
        # use a context manager to watch for the validation error being raised
        self.assertFieldOutput(EmailField, {'a@a.com': 'a@a.com'}, {'aaa': [u'Enter a valid email address.']})

    def test_register_sends_email(self):
        form = EmailUserCreationForm()
        form.cleaned_data = {
            'username': 'test',
            'email': 'test@test.com',
            'password1': 'test-pw',
            'password2': 'test-pw',
        }
        form.save()
        # Check there is an email to send
        self.assertEqual(len(mail.outbox), 1)
        # Check the subject is what we expect
        self.assertEqual(mail.outbox[0].subject, 'Welcome!')
