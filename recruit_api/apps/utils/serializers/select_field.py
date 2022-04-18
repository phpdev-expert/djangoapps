from rest_framework import serializers
from recruit_api.apps.utils.exceptions import RecruitException
from recruit_api.apps.utils.constants import SELECT_FIELD_SERIALIZER_LABEL


class SelectFieldSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super(SelectFieldSerializer, self).__init__(*args, **kwargs)
        model = self.context.get('model')
        if model:
            data = kwargs.get('data', None)
            if not data.get(SELECT_FIELD_SERIALIZER_LABEL, None):
                label_error_message = {
                    model: ["This field may not be blank."]
                }
                raise RecruitException(f'{model} field may not be blank', label_error_message)

    value = serializers.IntegerField(allow_null=True, required=False)
    label = serializers.CharField()


class SelectFieldIconUrlSerializer(serializers.Serializer):
    value = serializers.IntegerField(allow_null=True)
    label = serializers.CharField()
    icon_url = serializers.CharField()
