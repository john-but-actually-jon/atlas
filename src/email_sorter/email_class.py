from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any, List
from datetime import datetime
import re
import base64

from exceptions import InvalidSenderAddress


@dataclass
class Email:
    """
    Generic email class, for storing relevant email data

    Input Parameters:
    date: Date the email was received
    sender: Address the message was received from
    subect: Email subject line
    body: The decoded body of the email,
        not including attachments and non-text MIME types
    attachments: Descriptions of the attachments to the email #TODO

    """

    date: Union[str, datetime]
    body: Dict[str, str] = field(default_factory=lambda: {"": ""})
    receiver: str = ""
    sender: str = ""
    subject: str = ""
    attachments: Optional[list] = None

    def verify(self) -> None:
        email_address_regex = (
            r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
        )
        try:
            assert re.fullmatch(email_address_regex, self.sender) is not None
        except AssertionError:
            raise InvalidSenderAddress(f"Email address {self.sender} not verifiable.")

    def __str__(self):
        return_string = "\n".join(
            [
                f"""
                {key}:\n {value}
            """
                for key, value in self.__dict__.items()
            ]
        )
        return return_string

    def tokenize(self):
        raise NotImplementedError


@dataclass
class EmailParser:
    raw_email: Dict[str, Any]
    desired_header_keys: List[str] = field(
        default_factory=lambda: ["From", "To", "Date"]
    )
    valid_body_mime_types: List[str] = field(
        default_factory=lambda: ["text/plain", "text/html"]
    )

    @staticmethod
    def urlsafe_b64decoder(input: str) -> str:
        """Decodes the encoded body of an email"""
        return str(base64.urlsafe_b64decode(input + "=" * (4 - len(input) % 4)))

    def attachments_handler(self):
        raise NotImplementedError

    def parse(self) -> Email:
        """Return an Email object from a raw email output from the Gmail API"""
        parsed_headers = {
            header["name"]: header["value"]
            for header in self.raw_email["payload"]["headers"]
            if header["name"] in self.desired_header_keys
        }
        body = {
            part["mimeType"]: self.urlsafe_b64decoder(part["body"]["data"])
            for part in self.raw_email["payload"]["parts"]
            if part["mimeType"] in self.valid_body_mime_types
        }
        return Email(
            date=parsed_headers["Date"],
            receiver=parsed_headers["To"].strip("<>"),
            sender=parsed_headers["From"].split(" ")[1].strip("<>"),
            subject=self.raw_email["snippet"],
            body=body,
        )


@dataclass
class TokenizedEmail(Email):
    pass


if __name__ == "__main__":
    from src.generic_google_api_service import google_api_service
    from src.config import CREDENTIALS, SCOPES

    with google_api_service(
        client_secret_file=CREDENTIALS,
        api_name="gmail",
        api_version="v1",
        scopes=SCOPES,
    ) as gmail:
        _email = (
            gmail.users()
            .messages()
            .get(userId="me", id="18388d78eeafd544", metadataHeaders="full")
            .execute()
        )

    email = EmailParser(_email).parse()

    print(email)
