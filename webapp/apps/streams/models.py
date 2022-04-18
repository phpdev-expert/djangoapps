from django.contrib.postgres.fields import ArrayField
from django.db import models

from djutil.models import TimeStampedModel
from webapp.apps.metrics.models import Account


class Board(TimeStampedModel):
    """
    A tab to contain a list of streams components
    name: Name of the board
    user_id: The user id the board belongs to
    streams_position: A list of stream object id's to maintain the order of their position in the dashboard.
    archived_at: Stores the datetime when the board was deleted.
    """

    name = models.CharField(max_length=256, default="New Board")
    user_id = models.PositiveIntegerField(db_index=True)
    streams_position = ArrayField(models.PositiveIntegerField(blank=True), default=list)
    archived_at = models.DateTimeField(default=None, null=True, blank=True)


class Stream(TimeStampedModel):
    """
    A stream containing the list of events on a site
    name: Name of the stream
    type: Type of board [HOME, MENTIONS, MY_TWEETS, LIKES, RETWEETS, SCHEDULED, NEW_FOLLOWERS, KEYWORD, LISTS]
    account_id: A reference ID to the metrics account table containing the page and network
    terms: keywords/search terms used to filter content
    archived_at: Stores the datetime when the board was deleted.
    board_id: The ID of the board to which the stream belongs to
    user_id: The user id the board belongs to
    """

    name = models.CharField(max_length=256)
    type = models.CharField(max_length=64)
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, null=False, blank=False,
    )
    terms = ArrayField(models.CharField(blank=True, max_length=256), default=list)
    archived_at = models.DateTimeField(default=None, null=True, blank=True)
    board = models.ForeignKey(
        Board, on_delete=models.CASCADE, null=False, blank=False, related_name='streams'
    )
    user_id = models.PositiveIntegerField(db_index=True, null=False, blank=False,)