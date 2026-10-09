"""Editable user-profile API for the local OTP demonstration flow."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.dependencies import get_request_database_session
from backend.app.infrastructure.db.models import UserProfile

router = APIRouter(prefix="/profiles", tags=["profiles"])

_DIGIT_TRANSLATION = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_ALLOWED_INCOME = {
    "",
    "up-to-22",
    "22-to-50",
    "50-to-80",
    "80-to-120",
    "120-to-160",
    "160-to-250",
    "250-to-500",
    "500-to-1000",
    "over-1000",
}
_ALLOWED_GENDER = {"", "female", "male"}


def normalize_phone(value: str) -> str:
    digits = value.translate(_DIGIT_TRANSLATION)
    if len(digits) == 9 and digits.isdigit():
        digits = f"09{digits}"
    if len(digits) != 11 or not digits.startswith("09") or not digits.isdigit():
        raise ValueError("phone must be an Iranian mobile number")
    return digits


class ProfilePayload(BaseModel):
    phone: str
    firstName: str = Field(default="", max_length=60)
    lastName: str = Field(default="", max_length=60)
    income: str = Field(default="", max_length=40)
    job: str = Field(default="", max_length=40)
    gender: str = Field(default="", max_length=10)
    avatar: str | None = Field(default=None, max_length=140_000)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        return normalize_phone(value)

    @field_validator("income")
    @classmethod
    def validate_income(cls, value: str) -> str:
        if value not in _ALLOWED_INCOME:
            raise ValueError("income is not supported")
        return value

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        if value not in _ALLOWED_GENDER:
            raise ValueError("gender is not supported")
        return value

    @field_validator("avatar")
    @classmethod
    def validate_avatar(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith("data:image/"):
            raise ValueError("avatar must be an image data URL")
        return value


def _response(profile: UserProfile) -> ProfilePayload:
    return ProfilePayload(
        phone=profile.phone,
        firstName=profile.first_name,
        lastName=profile.last_name,
        income=profile.income,
        job=profile.job,
        gender=profile.gender,
        avatar=profile.avatar_data_url,
    )


def _database_session(session: Session | None) -> Session:
    if session is None:
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Profile service is temporarily unavailable."
        )
    return session


@router.get("/{phone}", response_model=ProfilePayload)
def read_profile(
    phone: str, session: Annotated[Session | None, Depends(get_request_database_session)]
) -> ProfilePayload:
    record = _database_session(session).get(UserProfile, normalize_phone(phone))
    if record is None:
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Profile was not found.")
    return _response(record)


@router.put("", response_model=ProfilePayload)
def upsert_profile(
    payload: ProfilePayload, session: Annotated[Session | None, Depends(get_request_database_session)]
) -> ProfilePayload:
    active_session = _database_session(session)
    record = active_session.get(UserProfile, payload.phone)
    if record is None:
        record = UserProfile(phone=payload.phone)
        active_session.add(record)
    record.first_name, record.last_name = payload.firstName, payload.lastName
    record.income, record.job, record.gender = payload.income, payload.job, payload.gender
    record.avatar_data_url = payload.avatar
    active_session.commit()
    active_session.refresh(record)
    return _response(record)
