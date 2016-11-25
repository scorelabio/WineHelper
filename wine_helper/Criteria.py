class Criteria:
    """
    This class represents a criterion.
    """

    def __init__(self, name, value):
        self.name = name
        self.value = value


    def get_name (self):
        return self.name


    def get_value (self):
        return self.value


    def set_name (name):
        self.name = name


    def set_value (value):
        self.value = value
