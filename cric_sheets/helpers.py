def first(collection, *, default=None):
    try:
        return next(iter(collection))
    except StopIteration:
        return default
        
