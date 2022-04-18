from recruit_api.apps.utils.operations import (RecruitOperations, SelectFieldOperations)
from recruit_api.apps.utils.constants import (SELECT_FIELD_SERIALIZER_LABEL, SELECT_FIELD_SERIALIZER_VALUE)
from recruit_api.apps.client.models import Client
from recruit_api.apps.client.serializers import ClientListSerializer


class ClientOperations(RecruitOperations):

    def get_as_select_list(self, detail_required=True, none_required=True):
        clients = Client.objects.all().order_by('name')
        _clients = []
        if none_required:
            none = SelectFieldOperations().get_none_option()
            if detail_required:
                none['detail'] = {}
            _clients.append(none)
        for client in clients:
            _client = {
                SELECT_FIELD_SERIALIZER_VALUE: client.id,
                SELECT_FIELD_SERIALIZER_LABEL: client.name
            }
            if detail_required:
                _client['detail'] = ClientListSerializer(client, many=False).data
            _clients.append(_client)
        return _clients
