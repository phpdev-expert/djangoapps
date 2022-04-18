from .recruit_object import RecruitObject
from recruit_api.apps.utils.constants import SELECT_FIELD_SERIALIZER_LABEL


class SelectFieldAnnotateModel(RecruitObject):
    def __init__(self):
        self.model = None
        self.query_set = None
        self.id_field = 'id'
        self.text_field = 'name'
        self.icon_url = None
        self.many = True
        self.order_by = SELECT_FIELD_SERIALIZER_LABEL
