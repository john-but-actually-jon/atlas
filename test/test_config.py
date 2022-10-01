"""
For defining test fixtures and edge cases for use during testing.
"""

import pytest
from random import randint

from src.generic_google_api_service import google_api_service
from src.config import CREDENTIALS, SCOPES


@pytest.fixture
def test_email():
    """Random, raw Email response"""
    with google_api_service(CREDENTIALS, "gmail", "v1", SCOPES) as gmail:
        rand_email_id = (
            gmail.users()
            .messages()
            .list(userId="me")
            .execute()["messages"][randint(0, 20)]["id"]
        )

        email = (
            gmail.users()
            .messages()
            .get(userId="me", id=rand_email_id, metadataHeaders="full")
            .execute()
        )
    return email
