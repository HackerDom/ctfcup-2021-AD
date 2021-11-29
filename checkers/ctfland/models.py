from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel


class UserRole(Enum):
    Visitor = 0,
    Moderator = 1,


@dataclass(frozen=True)
class RegisterRequest(BaseModel):
    login: str
    password: str
    document: str
    role: UserRole


class CreateParkRequest(BaseModel):
    name: str
    description: str
    email: str
    max_visitors: int
    attraction_block: str
    is_public: bool


class AddAttractionRequest(BaseModel):
    name: str
    description: str
    cost: int
    ticket: str
