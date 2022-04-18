from rest_framework.authentication import TokenAuthentication


class RecruitAuthentication(TokenAuthentication):
    keyword = "Bearer"
