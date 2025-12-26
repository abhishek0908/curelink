from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")

class APIError(BaseModel):
    code: str
    message: str

class APIResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[APIError] = None

    @classmethod
    def success_response(cls, data: T = None, message: str = "Success"):
        return cls(success=True, message=message, data=data, error=None)

    @classmethod
    def error_response(cls, code: str, message: str):
        return cls(
            success=False,
            message=message,
            data=None,
            error=APIError(code=code, message=message)
        )
