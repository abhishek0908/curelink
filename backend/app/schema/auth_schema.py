from pydantic import BaseModel,EmailStr

class LoginRequest(BaseModel):
    email:EmailStr

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    user_email:str
    is_verified:bool
    onboarding_completed:bool
