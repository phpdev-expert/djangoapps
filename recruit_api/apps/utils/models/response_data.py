from .recruit_object import RecruitObject


class ResponseData(RecruitObject):
    def __init__(self):
        self.message = ""
        self.result = None
        self.successful = False
        self.errors = None
