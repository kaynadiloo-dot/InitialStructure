from src.db.models.inversor_model import Inversor
from src.dtos.inversor_dto import InversorResponseDTO


def to_inversor_response(inversor: Inversor) -> InversorResponseDTO:
    return InversorResponseDTO.model_validate(inversor)
