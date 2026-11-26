from sqlalchemy.orm import Session

from src.db.models.favorito_model import Favorito


class FavoritoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **datos) -> Favorito:
        favorito = Favorito(**datos)
        self.db.add(favorito)
        self.db.commit()
        self.db.refresh(favorito)
        return favorito

    def get_by_id(self, inversor_id: int, activo_id: int) -> Favorito | None:
        return self.db.get(Favorito, (inversor_id, activo_id))

    def delete(self, favorito: Favorito) -> None:
        self.db.delete(favorito)
        self.db.commit()
