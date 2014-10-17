from django.test import TestCase
from mock import patch, Mock
from cards.models import Card
from cards.utils import create_deck, get_random_comic


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
