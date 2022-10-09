import os
from dataclasses import dataclass, field
from src import config as cfg
from src.config import config_load
from googleapiclient.discovery import Resource
from email_class import Email
import json
from pathlib import Path
from typing import List, Dict, Any, Literal, Optional

from keybert import KeyBERT
from nltk.corpus import stopwords

stop_words = set(stopwords.words("english"))


logger = cfg.logger
credentials_path = cfg.CREDENTIALS
scopes = cfg.SCOPES


@dataclass
class EmailRetriever:
    """
    Class that retrieves the desired number of emails using an existing
    google api gmail client.

    Parameters:
        - `gmail_service` (required): context manager defined
        generic_google_api_service.py. Any operations performed
        by this class should be performed strictly inside the gmail context
        - `number_of_emails` (optional): The number of emails to fetch
        using `fetch_email_ids`, default 10
        - `return_format` (optional): The desired format of the emails to
        be collected. One of ["full", "metadata", "minimal", "raw"].
        Default: "full"
        - `metadata_headers`: Usage unclear xd. Default: "full"
    """

    gmail_service: Resource
    number_of_emails: int = 10
    return_format: Literal["full", "metadata", "minimal", "raw"] = "full"
    metadata_headers: Literal["full"] = "full"

    def fetch_email_ids(self) -> List[Dict[str, str]]:
        """
        Returns a list of dictionaries with both message IDs and
        thread IDs for the top results for the latest number_of_emails

        Returns:
            - List of latest `self.number_of_emails` dictionaries with
            both message and thread IDs
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
        """
        Returns a list of raw email objects

        Parameters:
            - `email_ids` (optional): A list of the desired email IDs.
            If not supplied, the latest `number_of_emails` (defined
            at instance definition) is returned.

        Returns:
            - A list of raw email dictionaries, fetched directly
            from google gmail api
        """
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
                    metadataHeaders=self.metadata_headers,
                )
                .execute()
            )
            emails.append(email_response)
        return emails


@dataclass
class EmailClassifier:
    """
    Class that makes classifying emails by importance for training, test and
    validation data easier.

    Initial implementation uses the command line to output information in the
    email to the command line, then prompting the user to classify the email's
    importance on a scale from 0 to 4.

    Then it writes the emails along with there classification to a file in
    the datasets folder

    Parameters:
        - `emails` (required): A list of parsed `Email` objects, from which
        important information can be extracted.
        - `file_prefix` (required): The prefix of the file that the labelled
        email data is written to.
        - `file_type` (optional): Desired output file format. One of ["csv",
        "json"]. Default: "csv"
    """

    emails: List[Email]
    file_prefix: str
    file_type: Literal["csv", "json"] = "csv"
    dataset_path: str = os.path.join(os.getcwd(), "datasets")
    _processed_emails: List[Email] = field(default_factory=lambda: [])
    _file_name: str = "labelled-emails"
    keyword_extractor: KeyBERT = KeyBERT(model="all-mpnet-base-v2")
    config = config_load(Path(Path(__file__).parent, "config.yaml"))

    def _check_for_processed_emails(self) -> Optional[List[Email]]:
        """
        Check the datasets directory for emails that have already been classified

        Returns:
            - `_processed_emails`: Used in the `start_classification` call to
            filter out the emails from the dataset in question that have
            already been processed
        """
        file_name = os.path.join(
            os.getcwd(), ".datasets", self._file_name, self.file_type
        )
        if os.path.isfile(file_name):
            with open(file_name) as f:
                emails_with_labels = json.load(f)
            return emails_with_labels
        else:
            return None

    def summarize_email(self, email: Email) -> Dict[str, Any]:
        """
        Output a list of important features from an email, including the
        sender, receiver, date and the keywords from the email body, extracted
        using the nltk library

        Parameters:
            email (required): The email to be summarized

        Returns:
            returnValue: Returns a summary of the important information in an
            email. Which can be printed to the command line to assist with
            labelling
        """
        features = {}
        features["keywords"] = keyword_model.extract_keywords(
            email.body,
            stop_words="english",
            highlight=config.highlight,
            top_n=config.top_n,
            keyphrase_ngram_range=(config.n_gram_bottom, config.n_gram_top),
        )

        return features

    def start_classification(self, number_of_emails: Optional[int]) -> None:
        """
        Start the command line email classification process.

        Parameters:
            - `number_of_emails`: The number of emails to start with

        Returns:
            returnValue: This is a description of the returnValue
        """
        pass


if __name__ == "__main__":
    # with google_api_service(
    #     credentials_path, "gmail", "v1", scopes, pickle_prefix="mail-client"
    # ) as gmail:
    #     retriever = EmailRetriever(gmail_service=gmail, number_of_emails=50)
    #     print(retriever.fetch_email_ids())
    from src.config import config_load
    from pathlib import Path

    confpath = Path(Path(__file__).parent, "config.yaml")
    print(confpath)
    config = config_load(confpath).email_ranking.keybert_params

    print(config)

    with open(
        Path(Path(__file__).parent.parent.parent, ".datasets", "labelled_emails.json"),
        "r",
    ) as f:
        emails_with_labels = json.load(f)
        print(emails_with_labels[0])
    keyword_model = KeyBERT(model="all-mpnet-base-v2")
    keywords = keyword_model.extract_keywords(
        emails_with_labels[0]["body"],
        stop_words="english",
        highlight=config.highlight,
        top_n=config.top_n,
        keyphrase_ngram_range=(config.n_gram_bottom, config.n_gram_top),
    )
    print(keywords)
