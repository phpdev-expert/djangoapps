from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from webapp.apps.streams.models import Board, Stream


@receiver(post_save, sender=Stream)
def add_streams_position(sender, instance, created, **_kwargs):
    """
    Update stream_positions after create and after delete
    If stream is created, add it to streams_position
    If stream is archived, remote it from streams_position
    """

    board = Board.objects.get(id=instance.board_id)
    # TODO: test if id's have been updated

    # if stream is newly created append it to end of streams position
    if created:
        board.streams_position.append(instance.id)

    # if stream is archived remove it from streams position
    if instance.archived_at is not None:
        try:
            board.streams_position.remove(instance.id)
        except ValueError:
            pass  # ignore if value is not present

    board.save()