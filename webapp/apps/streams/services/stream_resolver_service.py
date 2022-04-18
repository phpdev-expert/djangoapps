from webapp.apps.streams import services  # used during eval
from webapp.apps.streams import models
from webapp.apps.streams.constants import KLASS_MAPPING


class StreamResolverService:
    """
    Takes in the stream instance and resolves the social network it should fetch from.
    Fetches the data according to the type, page and query and returns it in the correct format.
    """

    def __init__(self, stream: models.Stream):
        """ Initialize the right service class for streaming data """
        self.stream = stream
        self.account = stream.account
        klass = KLASS_MAPPING[self.account.type]
        if not klass:
            raise Exception("Klass not Defined")
        self.streamer = eval(klass)(self.account.token, self.account.token_secret)

    def fetch_data(self, **kwargs):
        """ Fetch data by type [HOME, RETWEETS, ...]"""
        # TODO: add tests for different types
        stream_type = self.stream.type.lower()
        terms = " ".join(
            self.stream.terms
        )  # ["keyword1", "keyword2"] -> "keyword1 keyword2"
        # The below line basically resolves to something like `twitter_service.keywords(q="hello", page=2)`
        return getattr(self.streamer, stream_type)(query=terms, **kwargs)