from sqlalchemy.orm import Session

from src.db.models.dividendo_model import Dividendo


class DividendoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **datos) -> Dividendo:
        dividendo = Dividendo(**datos)
        self.db.add(dividendo)
        self.db.commit()
        self.db.refresh(dividendo)
        return dividendo

    def get_by_id(self, dividendo_id: int) -> Dividendo | None:
        return self.db.get(Dividendo, dividendo_id)

    def update(self, dividendo: Dividendo, **datos) -> Dividendo:
        for campo, valor in datos.items():
            setattr(dividendo, campo, valor)
        self.db.commit()
        self.db.refresh(dividendo)
        return dividendo

    def delete(self, dividendo: Dividendo) -> None:
        self.db.delete(dividendo)
        self.db.commit()
