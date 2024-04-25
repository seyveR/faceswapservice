from pydantic import BaseModel


class callbackTemplate(BaseModel):
    secret: str
    user: int
    message: str | None = None
    imageUrl: str | None = None
    response_message: int | None = None
    additional: str | None = None


class SwapRequest(BaseModel):
    secret: str
    sourceUrl: str
    targetUrl: str
    callbackUrl: str
    callbackTemplate: callbackTemplate
