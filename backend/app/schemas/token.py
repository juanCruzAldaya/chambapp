from pydantic import BaseModel


class Token(BaseModel):
    """Respuesta del login: el JWT a usar como Bearer."""

    access_token: str
    token_type: str = "bearer"
