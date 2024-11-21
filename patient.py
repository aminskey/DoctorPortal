class Patient:
    def __init__(self, dict):
        self.name = dict["name"]
        self.height = dict["height"]
        self.age = dict["age"]

        self.cpr = dict["cpr"]
        self.bgInfo = dict["background"]
        self.img = dict["profile-pic"]

        self.wd = ""

