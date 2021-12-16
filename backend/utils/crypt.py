import os
from passlib.context import CryptContext
import re

# os.environ["D"] = "1"
# print(os.environ['D'])


class Validate:
    def __init__(self) -> None:
        self.pattern_password: re = re.compile(
            r'^(?=.*[0-9].*)(?=.*[a-z].*)(?=.*[A-Z].*)[0-9a-zA-Z$%!#^]{8,}$'
        )

    def password(self, password):
        return self.pattern_password.match(password)


class Encoder:
    def __init__(self) -> None:
        self.context = CryptContext(schemes=['bcrypt'])
        self.validate = Validate()

    def gen_hash_link(self, name) -> str:
        return str(self.context.hash(name))\
          .split('$')[-1]\
          .replace("/", 'slash')\
          .replace("\\", 'slash')

    def hash_password(self, password) -> str:
        if self.validate.password(password):
            return self.context.hash(password)
        raise ValueError("password")

    @property
    def gnerate_key(self) -> str:
        return os.urandom(32)
