from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    """
    Schema for receiving refresh token in JSON body.
    """
    refresh_token: str = Field(
        ...,
        description="The refresh token to generate a new access token."
    )