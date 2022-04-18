from django.conf import settings
from django_elasticsearch_dsl import Document, fields

# from django_elasticsearch_dsl.documents import DocType
from django_elasticsearch_dsl.registries import registry

from webapp.apps.metrics.models import AccountMetrics, AccountObject, Metrics, Account


INDEX = settings.ELASTICSEARCH_INDEX_NAMES[__name__]


ACCOUNT_PROP = {
    "id": fields.IntegerField(),
    "user_id": fields.TextField(),
    "page_id": fields.TextField(),
    "name": fields.TextField(),
    "type": fields.TextField(),
}


# class MyType(DocType):
#     content_json = fields.ObjectField()

#     def prepare_content_json(self, instance):
#         return instance.content_json


@registry.register_document
class AccountMetricsDocument(Document):
    # date = fields.DateField()
    account = fields.ObjectField(properties=ACCOUNT_PROP)
    metrics = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "name": fields.TextField(),
            "slug": fields.TextField(),
            "metric": fields.TextField(),
            "description": fields.TextField(),
            "fields": fields.ObjectField(),
        }
    )

    object_id = fields.ObjectField(
        properties={
            "id": fields.IntegerField(),
            "object_id": fields.TextField(),
            "object_type": fields.TextField(),
            "account": fields.ObjectField(properties=ACCOUNT_PROP),
            "title": fields.TextField(),
            "description": fields.TextField(),
            "data": fields.ObjectField(),
            "date_posted": fields.DateField(),
        }
    )

    class Index:
        name = INDEX
        settings = {"number_of_shards": 15, "number_of_replicas": 0}

    class Django:
        model = AccountMetrics
        fields = ["id", "date", "value", "value_type"]
        related_models = [Account, Metrics, AccountObject]

        # Ignore auto updating of Elasticsearch when a model is saved
        # or deleted:
        # ignore_signals = True

        # Don't perform an index refresh after every update (overrides global setting):
        # auto_refresh = False

        # Paginate the django queryset used to populate the index with the specified size
        # (by default it uses the database driver's default setting)
        # queryset_pagination = 5000
