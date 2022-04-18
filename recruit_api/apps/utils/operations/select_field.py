from django.db.models import F
from recruit_api.apps.utils.serializers import (SelectFieldSerializer, SelectFieldIconUrlSerializer)
from recruit_api.apps.utils.exceptions import InvalidSerializer
from recruit_api.apps.utils.constants import (SELECT_FIELD_SERIALIZER_LABEL, SELECT_FIELD_SERIALIZER_VALUE)


class SelectFieldOperations:

    def validate(self, data):
        serializer = SelectFieldSerializer(data=data)
        if serializer.is_valid():
            return True
        raise InvalidSerializer("Unable to validate Model: SelectFieldSerializer", serializer.errors)

    def cast(self, data):
        if type(data) == str:
            data = {SELECT_FIELD_SERIALIZER_VALUE: None, SELECT_FIELD_SERIALIZER_LABEL: data}
        return data

    def generate_data(self, annotate_model):
        """
        :param annotate_model: Instance of SelectFieldAnnotateModel
        :return: SelectFieldSerializer data
        """
        query_set = annotate_model.query_set
        if not query_set and annotate_model.model:
            query_set = annotate_model.model.objects\
                .annotate(**{SELECT_FIELD_SERIALIZER_VALUE: F(annotate_model.id_field),
                             SELECT_FIELD_SERIALIZER_LABEL: F(annotate_model.text_field)})
        else:
            query_set = query_set.annotate(**{SELECT_FIELD_SERIALIZER_VALUE: F(annotate_model.id_field),
                                              SELECT_FIELD_SERIALIZER_LABEL: F(annotate_model.text_field)})
        if annotate_model.order_by:
            query_set = query_set.order_by(SELECT_FIELD_SERIALIZER_LABEL)
        if not annotate_model.many:
            query_set = query_set.first()
        if annotate_model.icon_url:
            return SelectFieldIconUrlSerializer(query_set, many=annotate_model.many).data
        return SelectFieldSerializer(query_set, many=annotate_model.many).data

    def get_none_option(self):
        return {
                SELECT_FIELD_SERIALIZER_VALUE: -1,
                SELECT_FIELD_SERIALIZER_LABEL: 'None'
            }
