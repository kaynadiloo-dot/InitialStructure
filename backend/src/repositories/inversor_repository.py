from sqlalchemy.orm import Session

from src.db.models.inversor_model import Inversor


class InversorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **datos) -> Inversor:
        inversor = Inversor(**datos)
        self.db.add(inversor)
        self.db.commit()
        self.db.refresh(inversor)
        return inversor

    def get_by_id(self, inversor_id: int) -> Inversor | None:
        return self.db.get(Inversor, inversor_id)

    def update(self, inversor: Inversor, **datos) -> Inversor:
        for campo, valor in datos.items():
            setattr(inversor, campo, valor)
        self.db.commit()
        self.db.refresh(inversor)
        return inversor

    def delete(self, inversor: Inversor) -> None:
        self.db.delete(inversor)
        self.db.commit()
