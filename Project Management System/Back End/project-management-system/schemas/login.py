from pydantic import BaseModel


class LoginBase(BaseModel):
    username: str
    password: str

class LoginRequest(LoginBase):
    pass

class LoginResponse(LoginBase):
    id: int
    name: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True
