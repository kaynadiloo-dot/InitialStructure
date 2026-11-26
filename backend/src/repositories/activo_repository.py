from sqlalchemy.orm import Session

from src.db.models.activo_model import Activo


class ActivoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **datos) -> Activo:
        activo = Activo(**datos)
        self.db.add(activo)
        self.db.commit()
        self.db.refresh(activo)
        return activo

    def get_by_id(self, activo_id: int) -> Activo | None:
        return self.db.get(Activo, activo_id)

    def update(self, registro: Activo, **datos) -> Activo:
        for campo, valor in datos.items():
            setattr(registro, campo, valor)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def delete(self, activo: Activo) -> None:
        self.db.delete(activo)
        self.db.commit()
