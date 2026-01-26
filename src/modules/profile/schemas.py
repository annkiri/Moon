import re

from pydantic import BaseModel, Field, field_validator


class UserProfileEntry(BaseModel):
    """
    Modelo para validar datos del perfil de usuario.
    """

    key: str = Field(
        ...,
        description="Identificador único en formato snake_case (ej: 'user_name', 'favorite_color').",
    )
    value: str = Field(..., description="El dato o hecho real (ej: 'Andy', 'Azul').")
    category: str = Field(
        default="general",
        description="Agrupación lógica (ej: 'personal', 'dev', 'preferences').",
    )

    # REGLA DE VALIDACIÓN: Forzar snake_case en las claves
    @field_validator("key")
    @classmethod
    def validate_key_format(cls, v):
        if not re.match(r"^[a-z0-9_]+$", v):
            raise ValueError(
                "La clave debe ser snake_case (solo minúsculas, números y guiones bajos)."
            )
        return v
