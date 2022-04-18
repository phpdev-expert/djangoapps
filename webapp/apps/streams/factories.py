import factory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyInteger

from webapp.apps.streams import models


class BoardFactory(DjangoModelFactory):
    class Meta:
        model = models.Board

    name = factory.Sequence(lambda n: 'New Board %s' % n)
    user_id = 1
    streams_position = list(range(1, 4))
