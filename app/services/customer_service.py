from pymysql import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
import logging

logger = logging.getLogger(__name__)


class CustomerService:

    @staticmethod
    def create(db: Session, customer_data: CustomerCreate):
        customer_db = select(Customer).where(Customer.email == customer_data.email)
        if customer_db:
            raise ValueError(f"The customer with {customer_data.email} already exists!")
        new_customer = Customer(**customer_data.model_dump())
        try:
            db.add(new_customer)
            db.commit()
            db.refresh(new_customer)
            print()
        except IntegrityError as e:
            print(e)

    @staticmethod
    def update(db: Session, id: int, customer_data: CustomerUpdate):
        customer_db = db.get(Customer, id)
        if not customer_db:
            raise ValueError(f"The customer with {id} not exists!")
        update_customer = customer_data.model_dump(exclude_unset=True)
        for key, value in update_customer.items():
            setattr(customer_db, key, value)
        try:
            db.commit()
            db.refresh(customer_db)
            return customer_db
        except IntegrityError as e:
            db.rollback()
            logger.error("DATABSE INTEGRITY ERROR", e)
