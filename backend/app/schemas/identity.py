from enum import StrEnum
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.common import DTO


class Role(StrEnum):
    student = "student"
    teacher = "teacher"
    admin = "admin"


class Principal(DTO):
    id: UUID
    university: str
    role: Role = Role.student
    email_verified: bool = False


class Register(DTO):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    name: str = Field(min_length=1, max_length=120)
    university: str = Field(min_length=1, max_length=200)
    career: str = Field(min_length=1, max_length=200)


class Login(DTO):
    email: EmailStr
    password: str


class Token(DTO):
    access_token: str
    token_type: str = "bearer"


class Verification(DTO):
    token: str = Field(min_length=1)


class ResendVerification(DTO):
    email: EmailStr


class ProfileUpdate(DTO):
    name: str = Field(min_length=1, max_length=120)
    university: str = Field(min_length=1, max_length=200)
    career: str = Field(min_length=1, max_length=200)
    bio: str = Field(default="", max_length=2000)
    skills: list[str] = Field(default_factory=list, max_length=30)


class Profile(ProfileUpdate):
    id: UUID
    email: EmailStr
    role: Role
    email_verified: bool
