class InvalidConfigException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class InvalidSenderAddress(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
