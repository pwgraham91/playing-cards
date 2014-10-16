from time import sleep
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.forms import EmailField
from django.http import HttpResponseRedirect
from django.test import TestCase, LiveServerTestCase
from mock import patch, Mock
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.webdriver import WebDriver
from cards.forms import EmailUserCreationForm
from cards.models import Card, Player, WarGame
from cards.test_utils import run_pyflakes_for_package, run_pep8_for_package
from cards.utils import create_deck, get_random_comic

# run with python manage.py test


def max_num(number_one, number_two):
    if number_one >= number_two:
        return number_one
    else:
        return number_two


class BasicMathTestCase(TestCase):
    def test_math(self):
        a = 1
        b = 1
        self.assertEqual(a + b, 2)

#     def test_failing_case(self):
#         a = 1
#         b = 1
#         self.assertEqual(a+b, 1)
#


class UtilTestCase(TestCase):
    def test_create_deck_count(self):
        """Test that we created 52 cards"""
        create_deck()
        self.assertEqual(Card.objects.count(), 52)


class ModelTestCase(TestCase):
    def test_get_ranking(self):
        """Test that we get the proper ranking for a card"""
        card = Card.objects.create(suit=Card.CLUB, rank="jack")
        self.assertEqual(card.get_ranking(), 11)

    def create_war_game(self, user, result=WarGame.LOSS):
        WarGame.objects.create(result=result, player=user)

    def test_get_wins(self):
        user = Player.objects.create_user(username='test-user', email='test@test.com', password='password')
        self.create_war_game(user, WarGame.WIN)
        self.create_war_game(user, WarGame.WIN)
        self.assertEqual(user.get_wins(), 2)

    def test_get_losses(self):
        user = Player.objects.create_user(username='test-user', email='test@test.com', password='password')
        self.create_war_game(user, WarGame.LOSS)
        self.create_war_game(user, WarGame.LOSS)
        self.create_war_game(user, WarGame.LOSS)
        self.assertEqual(user.get_losses(), 3)


class ResultTestCase(TestCase):
    def test_result1(self):
        first_card = Card.objects.create(suit=Card.CLUB, rank="jack")
        second_card = Card.objects.create(suit=Card.SPADE, rank="jack")
        self.assertEqual(Card.get_war_result(first_card, second_card), 0)

    def test_result2(self):
        first_card = Card.objects.create(suit=Card.CLUB, rank="two")
        second_card = Card.objects.create(suit=Card.SPADE, rank="jack")
        self.assertEqual(Card.get_war_result(first_card, second_card), -1)

    def test_result3(self):
        first_card = Card.objects.create(suit=Card.CLUB, rank="jack")
        second_card = Card.objects.create(suit=Card.SPADE, rank="two")
        self.assertEqual(Card.get_war_result(first_card, second_card), 1)


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


class SyntaxTest(TestCase):
    def test_syntax(self):
        """
        Run pyflakes/pep8 across the code base to check for potential errors.
        """
        packages = ['cards']
        warnings = []
        # Eventually should use flake8 instead so we can ignore specific lines via a comment
        for package in packages:
            warnings.extend(run_pyflakes_for_package(package, extra_ignore=("_settings",)))
            warnings.extend(run_pep8_for_package(package, extra_ignore=("_settings",)))
        if warnings:
            self.fail("{0} Syntax warnings!\n\n{1}".format(len(warnings), "\n".join(warnings)))


class ViewTestCase(TestCase):
    def setUp(self):
        create_deck()

    def create_war_game(self, user, result=WarGame.LOSS):
        WarGame.objects.create(result=result, player=user)

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertIn('<p>Suit: spade, Rank: two</p>', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_faq_page(self):
        response = self.client.get(reverse('faq'))
        self.assertIn('<p>Q: Can I win real money on this website?</p>\n    <p>A: Nope, this is not real, sorry.</p>',
                      response.content)

    def test_card_filters(self):
        response = self.client.get(reverse('filters'))
        self.assertIn('Capitalized Suit: 3 <br>\n            Uppercased Rank: SEVEN\n        </p>', response.content)

    def test_register_page(self):
        username = 'new-user'
        data = {
            'username': username,
            'email': 'test@test.com',
            'password1': 'test',
            'password2': 'test'
        }
        response = self.client.post(reverse('register'), data)

        # Check this user was created in the database
        self.assertTrue(Player.objects.filter(username=username).exists())

        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        # does the url location end with profile (cards.com/profile)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    def login_page(self):
        username = 'new-user'
        data = {
            'username': username,
            'password': 'password'
        }
        response = self.client.post(reverse('login'), data)

        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        # does the url location end with profile (cards.com/profile)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    def test_profile_page(self):
        # Create user and log them in
        password = 'passsword'
        user = Player.objects.create_user(username='test-user', email='test@test.com', password=password)
        self.client.login(username=user.username, password=password)

        # Set up some war game entries
        self.create_war_game(user)
        self.create_war_game(user, WarGame.WIN)

        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('profile'))
        self.assertInHTML('<p>Your email address is {}</p>'.format(user.email), response.content)
        self.assertEqual(len(response.context['games']), 2)

    @patch('cards.utils.requests')
    def test_xkcd_page(self, mock_requests):
        mock_comic = {
            'num': 1433,
            'year': "2014",
            'safe_title': "Lightsaber",
            'alt': "A long time in the future, in a galaxy far, far, away.",
            'transcript': "An unusual gamma-ray burst originating from somewhere across the universe.",
            'img': "http://imgs.xkcd.com/comics/lightsaber.png",
            'title': "Lightsaber",
        }
        mock_response = Mock()
        mock_requests.get.return_value = mock_response
        mock_response.status_code = 200
        mock_response.json.return_value = mock_comic
        self.assertEqual(get_random_comic()['num'], 1433)
        self.assertEqual(get_random_comic()['year'], "2014")


class SeleniumTests(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        Player.objects.create_superuser('superuser', 'superuser@test.com', 'mypassword')
        super(SeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(SeleniumTests, cls).tearDownClass()

    def test_admin_login(self):
        # Create a superuser

        # let's open the admin login page
        self.selenium.get("{}{}".format(self.live_server_url, reverse('admin:index')))
        self.selenium.find_element_by_name('username').send_keys('superuser')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys('mypassword')

        # Submit the form
        password_input.send_keys(Keys.RETURN)
        # sleep for half a second to let the page load
        sleep(.5)

        # We check to see if 'Site administration' is now on the page, this means we logged in successfully
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('Site administration', body.text)

    def admin_login(self):
        # Create a superuser
        Player.objects.create_superuser('superuser', 'superuser@test.com', 'mypassword')

        # let's open the admin login page
        self.selenium.get("{}{}".format(self.live_server_url, reverse('admin:index')))

        # let's fill out the form with our superuser's username and password
        self.selenium.find_element_by_name('username').send_keys('superuser')
        password_input = self.selenium.find_element_by_name('password')
        password_input.send_keys('mypassword')

        # Submit the form
        password_input.send_keys(Keys.RETURN)

    def test_admin_create_card(self):
        self.admin_login()

        # We can check that our Card model is registered with the admin and we can click on it
        # Get the 2nd one, since the first is the header
        self.selenium.find_elements_by_link_text('Cards')[1].click()

        # Let's click to add a new card
        self.selenium.find_element_by_link_text('Add card').click()
        self.selenium.find_element_by_name('rank').send_keys("ace")
        suit_dropdown = self.selenium.find_element_by_name('suit')
        for option in suit_dropdown.find_elements_by_tag_name('option'):
            if option.text == "heart":
                option.click()
        self.selenium.find_element_by_css_selector("input[value='Save']").click()
        sleep(.5)
        # Check to see we get the card was added success message
        body = self.selenium.find_element_by_tag_name('body')
        self.assertIn('The card "ace of hearts" was added successfully', body.text)

    def test_login(self):
        self.selenium.get("{}{}".format(self.live_server_url, reverse('login')))
        self.selenium.find_element_by_id('id_username').send_keys("superuser")
        self.selenium.find_element_by_id('id_password').send_keys("mypassword")
        self.selenium.find_element_by_css_selector("input[value='Log in']").click()
        sleep(5)
