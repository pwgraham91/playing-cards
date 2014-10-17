from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from cards.models import WarGame, Player
from cards.utils import create_deck

__author__ = 'GoldenGate'
from django.test import TestCase


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

    # not working for some reason, just use selenium
    #
    # def test_login_page(self):
    #     username = 'new-user'
    #     data = {
    #         'username': username,
    #         'password': 'password'
    #     }
    #     response = self.client.post(reverse('login'), data)
    #
    #     # Check it's a redirect to the profile page
    #     self.assertIsInstance(response, HttpResponseRedirect('profile'))
    #     # does the url location end with profile (cards.com/profile)
    #     self.assertTrue(response.get('location').endswith(reverse('profile')))

    def test_profile_page(self):
        # Create user and log them in
        password = 'password'
        user = Player.objects.create_user(username='test-user', email='test@test.com', password=password)
        self.client.login(username=user.username, password=password)

        # Set up some war game entries
        self.create_war_game(user)
        self.create_war_game(user, WarGame.WIN)

        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('profile'))
        # self.assertIn('<p>Your email address is {}</p>'.format(user.email), response.content)
        self.assertIn('<p>Hi {}, you have {} wins, {} ties and {} losses.</p>'.format(user.username, user.wins, user.ties, user.losses), response.content)
        self.assertEqual(len(response.context['games']), 2)
