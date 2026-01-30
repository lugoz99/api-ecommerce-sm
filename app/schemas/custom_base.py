from pydantic import BaseModel, ConfigDict


class CustomBase(BaseModel):
    model_config = ConfigDict(
        # Permite crear el modelo a partir de objetos, no solo de diccionarios.
        from_attributes=True,
        validate_assignment=True,
        str_strip_whitespace=True,  # delete
    )
