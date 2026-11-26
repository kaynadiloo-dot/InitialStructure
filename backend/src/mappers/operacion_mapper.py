from src.db.models.operacion_model import Operacion
from src.dtos.operacion_dto import OperacionResponseDTO


def to_operacion_response(operacion: Operacion) -> OperacionResponseDTO:
    return OperacionResponseDTO.model_validate(operacion)
