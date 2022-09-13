from dataclasses import dataclass, fields
from typing import Optional
import re
import nltk

from .exceptions import InvalidSenderAddress




@dataclass
class Email:
    sender: str = ''
    subject: str = ''
    body: str = ''
    attachments: Optional[list] = None

    def verify(self) -> None:
        email_address_regex = '([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
        try:
            assert re.fullmatch(email_address_regex, self.sender) is not None
        except AssertionError:
            raise InvalidSenderAddress(f'Email address {self.sender} not verifiable.')

    def __str__(self):
        return_string = "\n".join([f'{key}:\n {value}' for key, value in self.__dict__.items()])
        return return_string

    def tokenize(self):
        raise NotImplementedError

@dataclass
class TokenizedEmail(Email):
    pass
