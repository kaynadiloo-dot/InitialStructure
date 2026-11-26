from pydantic import BaseModel

from src.schemas.inversiones_tipos import IdPositivo


class CreateFavoritoSchema(BaseModel):
    inversor_id: IdPositivo
    activo_id: IdPositivo
