from rest_framework import status
from rest_framework.decorators import api_view
from recruit_api.apps.utils.models import ResponseData
from recruit_api.apps.utils.api.response import RecruitResponse
from recruit_api.apps.candidate.operations.third_party import ThirdPartyOperations

from rest_framework.views import APIView
from recruit_api.apps.candidate.serializers.third_party import ThirdPartySerializer
from rest_framework.response import Response
from django.shortcuts import render,redirect,get_object_or_404
from recruit_api.apps.candidate.models.candidate import ThirdParty
from rest_framework import generics
class ThirdPartyAPIView(APIView):
    serializer_class = ThirdPartySerializer
    def get(self,request):
        try:
            data = ResponseData()
            data.result = ThirdPartyOperations().get_as_select_list(detail_required=False)
            data.message = "Third Party list has been fetched successfully."
            return RecruitResponse.get_success_response(status.HTTP_200_OK, data)
        except Exception as ex:
            return RecruitResponse.get_exception_response(ex)

    def post(self,request):
        data = ResponseData()
        serializer=ThirdPartySerializer(data=request.data);
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ThirdPartyAPIUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = ThirdParty.objects.all()
    serializer_class = ThirdPartySerializer

class ThirdPartyDetail(APIView):
    """
    Retrieve, update or delete a person instance.
    """

    def get_object(self, pk):
        try:
            return ThirdParty.objects.get(pk=pk)
        except ThirdParty.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        third_party = self.get_object(pk)
        serializer = ThirdPartySerializer(third_party)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        third_party = self.get_object(pk)
        serializer = ThirdPartySerializer(third_party, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        third_party = self.get_object(pk)
        third_party.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
