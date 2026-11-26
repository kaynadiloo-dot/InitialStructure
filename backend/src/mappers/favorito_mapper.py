from src.db.models.favorito_model import Favorito
from src.dtos.favorito_dto import FavoritoResponseDTO


def to_favorito_response(favorito: Favorito) -> FavoritoResponseDTO:
    return FavoritoResponseDTO.model_validate(favorito)
