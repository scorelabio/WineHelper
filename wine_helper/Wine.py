class Wine:
    """
    This class represents a Wine.
    """

    def __init__(self, appellation, name, vintage, price, global_score, color):
        self.appellation = appellation
        self.name = name
        self.vintage = vintage
        self.price = price
        self.global_score = global_score
        self.color = color


    def get_appellation(self):
        return self.appellation


    def get_name(self):
        return self.name


    def get_vintage(self):
        return self.vintage


    def get_price(self):
        return self.price


    def get_global_score(self):
        return self.global_score


    def get_color(self):
        return self.color


    def __str__(self):
        return ("Wine("
                "appellation: '{0}',"
                " name: '{1}',"
                " vintage: {2},"
                ")"
                ).format(
                    self.appellation,
                    self.name,
                    str(self.vintage)
                )
