from django.db import transaction
from recruit_api.apps.job.models.job import HiringManagerTitle
from recruit_api.apps.utils.operations import RecruitOperations
from recruit_api.apps.job.serializers.job import HiringManagerTitleSerializer
from recruit_api.apps.utils.exceptions import InvalidSerializer


class JobTitleOperations(RecruitOperations):

    def __init__(self):
        self.title = None

    def get(self, pk):
        if not self.title or self.title.pk != pk:
            self.title =HiringManagerTitle.objects.get(pk=pk)
        return self.title

    def create_or_update(self, data):
        print('VALIDATING')
        print(data);
        try:
            serializer =HiringManagerTitleSerializer(data=data)
            if serializer.is_valid():
                _id = data.get("id", None)
                if _id:
                    title = self.get(_id)
                    return serializer.update(title, serializer.validated_data)
                return serializer.save()
            raise InvalidSerializer("Unable to validate Serializer: Title", serializer.errors)
        except Exception as ex:
            raise ex

    def create_or_update_multiple(self, titles):
        try:
            with transaction.atomic():
                if type(titles) == str:
                    titles = [titles]
                _titles = []
                for title in titles:
                    print("Tuutles")
                    print(title)
                    if type(title) == str:
                        title = {'title': title}
                    title = self.create_or_update(title)
                    _titles.append(title.pk)
                return _titles
        except Exception as ex:
            raise ex
