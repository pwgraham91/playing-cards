__author__ = 'GoldenGate'

import factory
from cards.models import Player, WarGame


class WarGameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'cards.WarGame'


class PlayerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'cards.Player'

class CardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'cards.Card'
