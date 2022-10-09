from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any, List
from datetime import datetime
import re
import base64
from bs4 import BeautifulSoup

from src.exceptions import InvalidSenderAddress


@dataclass
class Email:
    """
    Generic email class, for storing relevant email data

    Parameters:
        - `date`: Date the email was received
        - `sender`: Address the message was received from
        - `subect`: Email subject line
        - `body`: The decoded body of the email,
        not including attachments and non-text MIME types
        - `attachments`: Descriptions of the attachments to the email #TODO

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
    """
    Class for converting raw email dictionary objects returned directly
    by the Google API service calls.

    Parameters:
        - `raw_email` (required): The raw email dictionary object to parse
        into an `Email` instance.
        - `desired_head_keys` (optional): List of headers that should be parsed.
        - `valid_body_mime_types` (optional): List of email part types to
        filter for relevant information
    """

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

    @staticmethod
    def html_body_parser(body: str) -> str:
        """
        A parser for HTML bodies which returns a plaintext string
        containing just the text from the body.

        Parameters:
            - `body` (required): the HTML body to parse into plaintext

        Returns:
            Returns: The plaintext content of the passed body. Excluding
            scripts and other HTML features
        """
        _body = BeautifulSoup(body, features="html.parser")

        # Remove script elements
        for script in _body(["script", "style"]):
            script.extract()

        text = _body.body.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = "\n".join(chunk for chunk in chunks if chunk)

        return text

    def body_handler(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = {}
        try:
            for part in payload["parts"]:
                # if part['mimeType'] in self.valid_body_mime_types:
                body.update(
                    {part["mimeType"]: self.urlsafe_b64decoder(part["body"]["data"])}
                )
        except KeyError:
            body.update(
                {payload["mimeType"]: self.urlsafe_b64decoder(payload["body"]["data"])}
            )
        return body

    def parse(self) -> Email:
        """Return an Email object from a raw email output from the Gmail API"""
        parsed_headers = {
            header["name"]: header["value"]
            for header in self.raw_email["payload"]["headers"]
            if header["name"] in self.desired_header_keys
        }
        body = self.body_handler(self.raw_email["payload"])
        for mime_type, part in body.items():
            if "html" in mime_type:
                body[mime_type] = self.html_body_parser(part)

        return Email(
            date=parsed_headers["Date"],
            receiver=parsed_headers["To"].split(" ")[-1].strip("<>"),
            sender=parsed_headers["From"].split(" ")[-1].strip("<>"),
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
            .get(userId="me", id="1838aae504781838", metadataHeaders="full")
            .execute()
        )

    email = EmailParser(_email).parse()

    print(email)
