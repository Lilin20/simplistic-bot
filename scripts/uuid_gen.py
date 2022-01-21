import string
import random


class UuidGen:
    def __init__(self):
        self.prefix = "uuid-"
        self.uuid = ""

    def build(self):
        self.uuid = ""
        self.uuid += self.prefix
        self.uuid += ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=20))
        return self.uuid


generator = UuidGen()
