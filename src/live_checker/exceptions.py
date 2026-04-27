from fastapi import HTTPException, status

class LinkNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found",
        )
