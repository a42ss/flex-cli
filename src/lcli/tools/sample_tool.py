class Calculator(object):
    """A simple calculator class."""

    def double(self, number):
        """Double the input -> twice"""
        return 2 * number

    def h(self):
        import json

        print(json.dumps(["double", "Calculator12"], sort_keys=True))
        exit(0)

    class Calculator2(object):
        """A simple calculator class."""

        def double(self, number):
            return 2 * number
