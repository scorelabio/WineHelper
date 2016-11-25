class Wine:
    def __init__(self, appellation, name, color, vintage, price, global_score):
        self.appellation = appellation
        self.name = name
        self.color = color
        self.vintage = vintage
        self.price = price
        self.global_score = global_score

    def get_appellation(self):
        return self.appellation

    def get_name(self):
        return self.name

    def get_vintage(self):
        return self.vintage

    def get_color(self):
        return self.color

    def get_price(self):
        return self.price

    def get_global_score(self):
        return self.global_score

    def __str__(self):
        return self.name + " (" + self.appellation + ")"

    def __repr__(self):
        return self.appellation
