from typing import Any

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")
    name: str = Field(min_length=1, max_length=200)
    language: str = "en"
    about_text: str = ""


class PhoneRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")


class OtpVerifyRequest(BaseModel):
    phone: str = Field(min_length=10, max_length=10, pattern=r"^\d{10}$")
    otp: str = Field(min_length=4, max_length=8)


class LanguageRequest(BaseModel):
    language: str = Field(min_length=2, max_length=16)


class ProfileUpdate(BaseModel):
    name: str | None = None
    language: str | None = None
    about_text: str | None = None
    age: int | None = Field(default=None, ge=1, le=120)
    gender: str | None = None
    state: str | None = None
    district: str | None = None
    occupation: str | None = None
    occupation_type: str | None = None
    annual_income: int | None = Field(default=None, ge=0)
    category: str | None = None
    is_entrepreneur: bool | None = None
    has_existing_business: bool | None = None
    has_land: bool | None = None
    citizenship: str | None = None


class ApplyRequest(BaseModel):
    scheme_id: str


class SchemeUpsert(BaseModel):
    id: str
    code: str | None = None
    name: str
    department: str | None = None
    description: str | None = None
    full_description: str | None = None
    deadline: str | None = None
    categories: list[str] = []
    target_groups: list[str] = []
    locations: list[str] = []
    benefits: list[str] = []
    constraints: list[dict[str, Any]] = []
    documents: list[dict[str, Any]] = []
    source: str = "admin"
