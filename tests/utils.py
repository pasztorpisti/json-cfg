

class WrapCallable(object):
    """
    With python3 the unittest framework calls the __getattr__ method of the callable
    with "__name__" parameter and this cases problems if the callable is something that
    implements __getattr__ but doesn't expect "__name__" as a parameter there.
    """
    def __init__(self, callable_):
        self.callable = callable_

    def __call__(self, *args, **kwargs):
        return self.callable(*args, **kwargs)
