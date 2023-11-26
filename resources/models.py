import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, HttpUrl, Field

from utils.date_utils import datetime_now


class JobSchema(BaseModel):
    title: str
    link: HttpUrl
    job_type: str
    posted_on: str
    workload: Optional[str]
    budget: Optional[str]
    duration: Optional[str]
    contractor_tier: str
    tier_label: Optional[str]
    description: str
    verification_status: Optional[str]
    skills: List[str]
    rating: str
    spendings: str
    country: str


class JobsSchemaList(BaseModel):
    jobs: List[JobSchema]


class ProfileSchema(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    account: str
    address: dict[str, str | None]
    first_name: Optional[str]
    last_name: Optional[str]
    full_name: Optional[str]
    birth_date: Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    picture_url: HttpUrl
    employment_status: Optional[str]
    employment_type: Optional[str]
    job_title: Optional[str]
    ssn: Optional[str]
    marital_status: Optional[str]
    gender: Optional[str]
    hire_date: Optional[str]
    termination_date: Optional[str]
    termination_reason: Optional[str]
    employer: Optional[str]
    base_pay: dict[str, str | None]
    pay_cycle: str
    platform_ids: dict[str, str | None]
    created_at: datetime = Field(default_factory=datetime_now)
    updated_at: Optional[datetime] = None
    metadata: dict[str, str] = {}


class JobsAndProfileSchema(BaseModel):
    jobs: List[JobSchema]
    profile: ProfileSchema
