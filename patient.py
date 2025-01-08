"""
*   AUTHOR:     SYED M. AMIN
*   PROJECT:    AI (ESCAPE ROOM AFLEVERING)
*   FILE:       patient.py
"""

import datetime
from dateutil.relativedelta import relativedelta

class Patient:
    def __init__(self, dict):

        self.name = dict["name"]
        self.height = dict["height"]

        self.cpr = dict["cpr"]
        self.bgInfo = dict["background"]
        self.img = dict["profile-pic"]

        self.wd = ""
        self.mri = dict["mri-scan"]
        self.dict = dict
        self.diag = dict["isdiagnosed"]
        self.post2000 = dict["post2000"]
        self.age = self.parseCpr(self.cpr)

    def parseCpr(self, cprnr: str):
        x = cprnr.split('-')[0]
        yrs = int(x[-2:]) + 2000 if self.post2000 else 1900
        mnth = int(x[2:4])
        days = int(x[:2])

        bday = datetime.datetime(yrs, mnth, days)
        return relativedelta(datetime.datetime.now(), bday)

