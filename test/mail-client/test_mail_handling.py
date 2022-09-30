import re

from src.email_sorter.email_class import Email, EmailParser

from test_config import test_email

email_regex = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")

def test_email_parser(test_email):
    # Test initialization
    parser = EmailParser(test_email)
    assert parser.raw_email == test_email

    #TODO: Test attachments functionality
    try:
        parser.attachments_handler()
    except NotImplementedError:
        pass

    # Test parsing functionality
    try:
        email = parser.parse()
    except Exception as e:
        raise e
    assert not email.attachments # Not implemented
    assert len(email.body) >= 1
    assert len(list(email.body.values())[0]) > 10
    assert re.match(email_regex, email.sender)



