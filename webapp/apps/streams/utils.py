import functools


def resolve_twitter_parameters(kwargs) -> dict:
    """
    Convert Pagination params to Tweepy compatible params
    i.e before_id -> max_id
    """
    return {
        "since_id": kwargs.get("after_id"),
        "max_id": kwargs.get("before_id"),
        "count": int(kwargs.get("size", 0)),
        "page": kwargs.get("page"),
        "query": kwargs.get("query"),
    }


def paginated_response(fn):
    """Decorator to parse params and result of a method"""

    def wrapper_fn(*args, **kwargs):
        kwargs = resolve_twitter_parameters(kwargs)
        result = fn(*args, **kwargs)
        return {
            "page": None,
            "size": len(result),
            "first_id": result.since_id,
            "next_id": result.max_id,
            "content": [item._json for item in result],
        }

    return wrapper_fn


def paginate_class(decorator):
    """Add the paginated response to every method of the class"""

    def decorate(cls):
        for func in dir(cls):
            if callable(getattr(cls, func)) and not func.startswith("__"):
                setattr(cls, func, decorator(getattr(cls, func)))
        return cls

    return decorate