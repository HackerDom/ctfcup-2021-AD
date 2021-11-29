from pydantic import BaseModel


class RegisterRequest(BaseModel):
    login: str
    password: str
    document: str


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
