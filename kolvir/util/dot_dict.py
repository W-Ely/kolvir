class DotDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for key, value in arg.items():
                    self[key] = value
        if kwargs:
            for key, value in kwargs.items():
                self[key] = value

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as ex:
            raise AttributeError(name) from ex

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def update(self, values):
        for key, value in values.items():
            super().__setitem__(key, value)
            self.__dict__.update({key: value})
