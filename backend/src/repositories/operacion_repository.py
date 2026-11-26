from sqlalchemy.orm import Session

from src.db.models.operacion_model import Operacion


class OperacionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **datos) -> Operacion:
        operacion = Operacion(**datos)
        self.db.add(operacion)
        self.db.commit()
        self.db.refresh(operacion)
        return operacion

    def get_by_id(self, operacion_id: int) -> Operacion | None:
        return self.db.get(Operacion, operacion_id)

    def update(self, operacion: Operacion, **datos) -> Operacion:
        for campo, valor in datos.items():
            setattr(operacion, campo, valor)
        self.db.commit()
        self.db.refresh(operacion)
        return operacion

    def delete(self, operacion: Operacion) -> None:
        self.db.delete(operacion)
        self.db.commit()
