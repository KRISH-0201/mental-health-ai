from pydantic import BaseModel


# -------------------------
# Chat Request
# -------------------------
class ChatRequest(BaseModel):
    text: str


# -------------------------
# User Login
# -------------------------
class UserLogin(BaseModel):
    username: str
    password: str


# -------------------------
# User Register (if you use it)
# -------------------------
class UserRegister(BaseModel):
    username: str
    password: str