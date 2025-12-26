from sqlmodel import SQLModel
from typing import List


class OnboardingCreateRequest(SQLModel):
    full_name: str
    age: int
    gender: str
    previous_diseases: List[str]
    current_symptoms: List[str]
    medications: List[str]
    allergies: List[str]
    additional_notes: str

class OnboardingUpdateRequest(SQLModel):
    full_name: str | None = None
    age: int | None = None
    gender: str | None = None
    previous_diseases: List[str] | None = None
    current_symptoms: List[str] | None = None
    medications: List[str] | None = None
    allergies: List[str] | None = None
    additional_notes: str | None = None


class OnboardingResponse(SQLModel):
    full_name: str | None
    age: int | None
    gender: str | None
    previous_diseases: List[str] | None
    current_symptoms: List[str] | None
    medications: List[str] | None
    allergies: List[str] | None
    additional_notes: str | None
    onboarding_completed: bool
class OnboardingStatusResponse(SQLModel):
    onboarding_completed: bool
