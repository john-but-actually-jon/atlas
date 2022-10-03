import pickle
import os
from typing import List, Optional, Dict

from src.config import logger


from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from google.auth.transport.requests import Request


def create_service(
    client_secret_file, api_name, api_version, scopes: Dict[str, List[str]], prefix=""
) -> Optional[Resource]:
    """
    Function for creating a Google API service. The service context manager
    (`google_api_service`) makes a direct call to this function and uses
    the resulting service object.

    Parameters:
        - `client_secret_file` (required): Path to the credentials file, defined in .env file. Download from your google project dashboard.
        - `api_name` (required): Name of the desired google service, e.g.
        "gmail"
        - `api_version` (required): Version of the API to use, format "v1".
        - `scopes` (required): Scopes required for each service, typically
        defined in .env file.
        - `pickle_prefix` (optional): The prefix for the authorization
        pickle files

    Returns:
    - Google API service, when service creation fails, none is returned.
    """

    client_secret_file = client_secret_file
    API_VERSION = api_version
    api_specific_scopes = [scope for scope in scopes[api_name]]

    cred = None
    working_dir = os.getcwd()
    token_dir = ".token_pickles"
    pickle_file = f".token_{api_name}_{api_version}{prefix}.pickle"

    # Check if token dir exists first, if not, create the folder
    if not os.path.exists(os.path.join(working_dir, token_dir)):
        os.mkdir(os.path.join(working_dir, token_dir))

    if os.path.exists(os.path.join(working_dir, token_dir, pickle_file)):
        with open(os.path.join(working_dir, token_dir, pickle_file), "rb") as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secret_file, api_specific_scopes
            )
            cred = flow.run_local_server()

        with open(os.path.join(working_dir, token_dir, pickle_file), "wb") as token:
            pickle.dump(cred, token)

    try:
        service = build(api_name, API_VERSION, credentials=cred)
        logger.debug(api_name, API_VERSION, "service created successfully")
        return service
    except Exception as e:
        print(e)
        logger.error(f"Failed to create service instance for {api_name}")
        os.remove(os.path.join(working_dir, token_dir, pickle_file))
        return None


class google_api_service:
    """
    Context manager for handling Google API services. Designed to help
    terminate services when no longer needed

    Parameters:
        - `client_secret_file` (required): Path to the credentials file, defined in .env file. Download from your google project dashboard.
        - `api_name` (required): Name of the desired google service, e.g.
        "gmail"
        - `api_version` (required): Version of the API to use, format "v1".
        - `scopes` (required): Scopes required for each service, typically
        defined in .env file.
        - `pickle_prefix` (optional): The prefix for the authorization
        pickle files
    """

    def __init__(
        self,
        client_secret_file: str,
        api_name: str,
        api_version: str,
        scopes: Dict[str, List[str]],
        pickle_prefix: str = "",
    ) -> None:
        try:
            self.service = create_service(
                client_secret_file, api_name, api_version, scopes, prefix=pickle_prefix
            )
            assert self.service
        except Exception as e:
            raise e

    def __enter__(self) -> Resource:
        return self.service

    def __exit__(self, type, value, traceback) -> None:
        if self.service:
            self.service.close()


if __name__ == "__main__":
    pass
