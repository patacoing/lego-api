from rest_framework import status
from rest_framework.response import Response


class ResponseNotFound(Response):
    def __init__(self, detail: str):
        super().__init__(
            status=status.HTTP_404_NOT_FOUND,
            data={
                "detail": detail
            }
        )


class ResponseBadRequest(Response):
    def __init__(self, detail: str):
        super().__init__(
            status=status.HTTP_400_BAD_REQUEST,
            data={
                "detail": detail
            }
        )