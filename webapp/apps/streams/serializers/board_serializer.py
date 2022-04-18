from rest_framework import serializers
from webapp.apps.streams.models import Board, Stream


class BoardSerializer(serializers.ModelSerializer):
    """
    Serializes the Board data

     Sample Payload:
     id: 1
     name: 'Pyxis Board'
     streams_position: 23, 56, 32
     """

    class Meta:
        model = Board
        fields = ('id', 'name', 'user_id', 'streams_position')
        extra_kwargs = {
            'user_id': {'read_only': True}
        }

    def to_internal_value(self, data):
        """
        Converts string list to python list.
        i.e '23, 45, 53' -> [23, 45, 53]
        """

        data = data.copy()
        if data.get('streams_position') is not None:
            streams_position = data['streams_position'].strip()
            try:
                if streams_position:
                    split_values = streams_position.split(',')
                    data['streams_position'] = [int(value) for value in split_values]
                else:
                    data['streams_position'] = []
            except ValueError:
                raise Exception("Invalid Value for streams_position.")

        return data

    def validate(self, attrs):
        """
        Check that the stream id's exist, belong to the board, and are active.
        Also check if all values are unique
        """
        value = attrs.get('streams_position')

        if value:
            # check if values are unique
            # TODO: test for unique ids
            if not len(value) == len(set(value)):
                raise serializers.ValidationError("streams_position contains duplicate ID's")

            # TODO: test that accessible objects are only added
            retrieved_obj_count = Stream.objects \
                .filter(board_id=self.instance.id) \
                .filter(archived_at=None) \
                .filter(id__in=value) \
                .count()

            if len(value) != retrieved_obj_count:
                raise serializers.ValidationError("streams_position values either dont exist or don't "
                                                  "belong to the user")

        return attrs