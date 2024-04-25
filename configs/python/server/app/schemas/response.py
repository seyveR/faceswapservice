from pydantic import BaseModel


class Message(BaseModel):
    message: str


class Error(Message):
    message: str = "Error"
    error: str
