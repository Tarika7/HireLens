from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """
    Data required to register a recruiter.
    """

    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """
    Data required to log in.
    """

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Data returned after registration.
    """

    id: int
    full_name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    """
    Response returned after successful login.
    """

    access_token: str
    token_type: str