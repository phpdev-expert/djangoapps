import json

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory

from webapp.apps.streams.views.boards_view import BoardsViewSet
from webapp.apps.streams.factories import BoardFactory


class BoardViewTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def test_create_board_view(self):
        view = BoardsViewSet.as_view({"post": "create"})
        name = "Something"
        streams_position = ""
        payload = {"name": name, "streams_position": streams_position}
        request = self.factory.post(
            "http://testserver/api/v2/streamapi/board/", payload
        )
        request.__dict__["user_details"] = {"id": 1}
        response = view(request).render()
        response_body = json.loads(response.content)
        assert response_body["name"] == name
        assert response_body["streams_position"] == []
        assert response.status_code == 201

    def test_update_board_view(self):
        new_object = BoardFactory(
            name="Something", streams_position=[45, 66, 21], user_id=1
        )
        view = BoardsViewSet.as_view({"put": "update"})

        payload = {
            "name": "Something Else",
            "user_id": 4,
        }
        request = self.factory.put(
            "http://testserver/api/v2/streamapi/board", payload
        )
        request.__dict__["user_details"] = {"id": 1}
        response = view(request, pk=new_object.id).render()
        response_body = json.loads(response.content)
        assert response_body["name"] == payload.get("name")
        assert response_body["streams_position"] == [45, 66, 21]
        assert response_body["user_id"] == 1
        assert response.status_code == status.HTTP_200_OK

    def test_delete_board_view(self):
        new_object = BoardFactory.create()
        view = BoardsViewSet.as_view({"delete": "destroy"})

        request = self.factory.delete(
            "http://testserver/api/v2/streamapi/board"
        )
        request.__dict__["user_details"] = {"id": 1}
        response = view(request, pk=new_object.id).render()
        response_body = json.loads(response.content)
        assert response_body["id"] == new_object.id
        assert response.status_code == status.HTTP_200_OK
        new_object.refresh_from_db()
        assert new_object.archived_at is not None

    def test_index_board_view(self):
        BoardFactory.create_batch(10)
        view = BoardsViewSet.as_view({"get": "list"})

        request = self.factory.get(
            "http://testserver/api/v2/streamapi/board"
        )
        request.__dict__["user_details"] = {"id": 1}
        response = view(request).render()
        response_body = json.loads(response.content)
        assert len(response_body) == 10
        assert response.status_code == status.HTTP_200_OK

    # TODO: stream position validation test