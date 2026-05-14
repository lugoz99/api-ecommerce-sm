from pydantic import computed_field
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Date
from app.database.session import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
import enum


class Gender(enum.Enum):
    male = "male"
    female = "female"
    other = "other"
    prefer_not_to_say = "prefer_not_to_say"


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)

    # formato YYYY-MM-DD
    date_birth: Mapped[date] = mapped_column(Date, nullable=True)

    url_photo: Mapped[str] = mapped_column(String(255), nullable=True)
    cloud_id: Mapped[str] = mapped_column(String(255), nullable=False)

    gender: Mapped[Gender] = mapped_column(
        Enum(Gender), default=Gender.prefer_not_to_say
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    # esta anotacion es para que SQLAlchemy sepa que esta propiedad no es una columna de la base de datos, sino un campo calculado

    @computed_field
    @property  # indica que es una propiedad de solo lectura
    def age(self) -> int | None:
        """Calcula la edad a partir de la fecha de nacimiento."""
        if not self.date_birth:
            return None

        # Convierte la fecha de nacimiento y calcula la edad
        birth_date = self.date_birth
        today = date.today()

        age = (
            today.year
            - birth_date.year
            - (
                # Resta 1 si el cumpleaños aún no ha ocurrido este año
                (today.month, today.day)
                < (birth_date.month, birth_date.day)
            )
        )

        return age
