from src.generic_google_api_service import google_api_service
from src.config import CREDENTIALS, SCOPES

if __name__ == "__main__":
    with google_api_service(
        client_secret_file=CREDENTIALS,
        api_name="gmail",
        api_version="v1",
        scopes=SCOPES,
    ) as gmail:

        print(gmail.users().getProfile(userId="me").execute())
