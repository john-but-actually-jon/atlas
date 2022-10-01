import re
from src.config import CREDENTIALS, SCOPES

from src.email_sorter.email_class import Email, EmailParser
from src.email_sorter.retrieve_emails import EmailRetriever
from src.generic_google_api_service import google_api_service

from test_config import test_email

email_regex = re.compile(
    r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+"
)


def test_email_parser(test_email):
    # Test initialization
    parser = EmailParser(test_email)
    assert parser.raw_email == test_email

    # TODO: Test attachments functionality
    try:
        parser.attachments_handler()
    except NotImplementedError:
        pass

    # Test parsing functionality
    try:
        email = parser.parse()
    except Exception as e:
        raise e
    assert not email.attachments  # Not implemented
    assert len(email.body) >= 1
    assert len(list(email.body.values())[0]) > 10
    assert re.match(email_regex, email.sender)


def test_mail_retrieval():
    test_number = 5
    with google_api_service(CREDENTIALS, "gmail", "v1", SCOPES) as gmail:
        retriever = EmailRetriever(gmail, test_number)
        email_ids = retriever.fetch_email_ids()
        emails = retriever.fetch_emails()
        manual_ids = [_id["id"] for _id in email_ids]
        emails_override = retriever.fetch_emails(email_ids=manual_ids)

    # Test id fetcher
    assert len(email_ids) == test_number
    for record in email_ids:
        assert "id" in list(record.keys())
        assert "threadId" in list(record.keys())

    # Test email fetcher
    assert emails == emails_override
