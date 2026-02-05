from app.schemas.custom_base import CustomBase


class CustomerCreate(CustomBase):
    last_names: str
    email: str
    phone_number: str
    address: str


class CustomerResponse(CustomBase):
    id: int
    last_names: str
    email: str
    phone_number: str
    address: str


class CustomerUpdate(CustomBase):
    id: int
    last_names: str
    email: str
    phone_number: str
    address: str
