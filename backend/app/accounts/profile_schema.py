"""Allowlisted editable profile contract shared by HTTP and persistence."""

import base64
import binascii

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .phone import normalize_phone

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


class ProfilePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
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
        if value is None:
            return None
        try:
            header, encoded = value.split(",", 1)
            image = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            raise ValueError("avatar must be an image data URL") from None
        signatures = {
            "data:image/png;base64": image.startswith(b"\x89PNG\r\n\x1a\n"),
            "data:image/jpeg;base64": image.startswith(b"\xff\xd8\xff"),
            "data:image/gif;base64": image.startswith((b"GIF87a", b"GIF89a")),
            "data:image/webp;base64": image.startswith(b"RIFF") and image[8:12] == b"WEBP",
        }
        if not signatures.get(header) or len(image) > 100 * 1024:
            raise ValueError("avatar must be a supported image of at most 100 KB")
        return value

    @field_validator("job")
    @classmethod
    def validate_job(cls, value: str) -> str:
        if value not in {
            "",
            "employee",
            "manager",
            "entrepreneur",
            "merchant",
            "freelancer",
            "teacher",
            "professional",
            "technical-worker",
            "driver",
            "farmer",
            "homemaker",
            "student",
            "retired",
            "unemployed",
            "other",
        }:
            raise ValueError("job is not supported")
        return value
