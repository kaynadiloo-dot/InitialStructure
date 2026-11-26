from sqlalchemy.orm import Session

from src.db.models.cuenta_model import Cuenta


class CuentaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **datos) -> Cuenta:
        cuenta = Cuenta(**datos)
        self.db.add(cuenta)
        self.db.commit()
        self.db.refresh(cuenta)
        return cuenta

    def get_by_id(self, cuenta_id: int) -> Cuenta | None:
        return self.db.get(Cuenta, cuenta_id)

    def update(self, cuenta: Cuenta, **datos) -> Cuenta:
        for campo, valor in datos.items():
            setattr(cuenta, campo, valor)
        self.db.commit()
        self.db.refresh(cuenta)
        return cuenta

    def delete(self, cuenta: Cuenta) -> None:
        self.db.delete(cuenta)
        self.db.commit()
