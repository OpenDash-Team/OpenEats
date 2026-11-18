from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator, model_validator

from backend.app.schemas.customer_request import Password

from .restaurant_request import Address, Name, Telephone





class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    email: EmailStr = Field(description="Email address, used to sign in.")
    password: Password = Field(description="Password")



class LoginResponse(BaseModel):
    status: str = "Login Successful"
    
    