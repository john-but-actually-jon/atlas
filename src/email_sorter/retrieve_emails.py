from dataclasses import dataclass
from src import config as cfg
from src.generic_google_api_service import google_api_service
from googleapiclient.discovery import Resource

from typing import List, Dict, Any, Literal, Optional

logger = cfg.logger
credentials_path = cfg.CREDENTIALS
scopes = cfg.SCOPES


@dataclass
class EmailRetriever:
    """
    Class that retrieves the desired number of emails using an existing
    google api gmail client.
    Use the context manager defined generic_google_api_service.py,
    and perform any operations using this class strictly inside said context.
    Once the emails have been fetched, you can leave the context manager.
    """

    gmail_service: Resource
    number_of_emails: int = 10
    return_format: Literal["full", "metadata", "minimal", "raw"] = "full"
    metadataHeaders: Literal["full"] = "full"

    def fetch_email_ids(self) -> List[Dict[str, str]]:
        """
        Returns a list of dictionaries with both message IDs and
        thread IDs for the top results for the latest number_of_emails
        """
        email_ids: List[Dict[str, str]] = []
        page_token = None
        while True:
            response = (
                self.gmail_service.users()
                .messages()
                .list(userId="me", pageToken=page_token)
                .execute()
            )
            email_ids = email_ids + response["messages"]
            page_token = response["nextPageToken"]
            if len(email_ids) >= self.number_of_emails:
                return email_ids[0 : self.number_of_emails]

    def fetch_emails(
        self, email_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """"""
        emails = []
        if email_ids:
            ids = [{"id": id} for id in email_ids]
        else:
            ids = self.fetch_email_ids()

        for full_id in ids:
            email_response = (
                self.gmail_service.users()
                .messages()
                .get(
                    userId="me",
                    id=full_id["id"],
                    format=self.return_format,
                    metadataHeaders=self.metadataHeaders,
                )
                .execute()
            )
            emails.append(email_response)
        return emails


if __name__ == "__main__":
    with google_api_service(
        credentials_path, "gmail", "v1", scopes, pickle_prefix="mail-client"
    ) as gmail:
        retriever = EmailRetriever(gmail_service=gmail, number_of_emails=50)
        print(retriever.fetch_email_ids())
