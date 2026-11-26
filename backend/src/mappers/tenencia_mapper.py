from src.db.models.tenencia_model import Tenencia
from src.dtos.tenencia_dto import TenenciaResponseDTO


def to_tenencia_response(tenencia: Tenencia) -> TenenciaResponseDTO:
    return TenenciaResponseDTO.model_validate(tenencia)
