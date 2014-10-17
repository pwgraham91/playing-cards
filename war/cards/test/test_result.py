from cards.models import Card

__author__ = 'GoldenGate'
from django.test import TestCase


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
