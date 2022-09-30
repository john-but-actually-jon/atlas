import os

from dotenv import load_dotenv
from logging import getLogger, INFO

from .exceptions import InvalidConfigException

logger = getLogger()
logger.setLevel(INFO)

load_dotenv()

try:
    assert (CREDENTIALS := str(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")))
except AssertionError:
    logger.error("Local path to credentials not defined!")
    raise InvalidConfigException
SCOPES = {"gmail": ["https://www.googleapis.com/auth/gmail.readonly"]}


if __name__ == "__main__":
    print(CREDENTIALS)
