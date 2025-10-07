from pydantic import BaseModel, Field, field_validator


class UserBaseSchema(BaseModel):
    username: str = Field(
        ...,
        max_length=255,
        description="Username of the user(maximum 64 characters)"
    )
    password: str = Field(
        ...,
        description="Password of the user"   
    )


class UserLoginSchema(UserBaseSchema):
    pass


class UserRegisterSchema(UserBaseSchema):
    confirm_password: str = Field(
        ...,
        description="Confirm Password of the user"   
    )

    @field_validator("confirm_password")
    def password_validator(cls, value, info):
        if value != info.data["password"]:
            raise ValueError("Passwords do not match")
        return value
            
