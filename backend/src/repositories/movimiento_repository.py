from sqlalchemy.orm import Session

from src.db.models.movimiento_model import Movimiento


class MovimientoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **datos) -> Movimiento:
        movimiento = Movimiento(**datos)
        self.db.add(movimiento)
        self.db.commit()
        self.db.refresh(movimiento)
        return movimiento

    def get_by_id(self, movimiento_id: int) -> Movimiento | None:
        return self.db.get(Movimiento, movimiento_id)

    def update(self, movimiento: Movimiento, **datos) -> Movimiento:
        for campo, valor in datos.items():
            setattr(movimiento, campo, valor)
        self.db.commit()
        self.db.refresh(movimiento)
        return movimiento

    def delete(self, movimiento: Movimiento) -> None:
        self.db.delete(movimiento)
        self.db.commit()
