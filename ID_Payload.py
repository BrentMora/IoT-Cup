from pydantic import BaseModel, field_validator
from typing import Optional

class ScannedIDPayload(BaseModel):
    uin:           str
    name:          Optional[str] = None
    dob:           Optional[str] = None
    location1:     Optional[str] = None
    location3:     Optional[str] = None
    zone:          Optional[str] = None
    postal_code:   Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    address_line3: Optional[str] = None

    @field_validator("uin")
    @classmethod
    def uin_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("UIN cannot be empty")
        return v.strip()