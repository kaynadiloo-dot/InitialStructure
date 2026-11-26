from sqlalchemy.orm import Session

from src.db.models.tenencia_model import Tenencia


class TenenciaRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **datos) -> Tenencia:
        tenencia = Tenencia(**datos)
        self.db.add(tenencia)
        self.db.commit()
        self.db.refresh(tenencia)
        return tenencia

    def get_by_id(self, cuenta_id: int, activo_id: int) -> Tenencia | None:
        return self.db.get(Tenencia, (cuenta_id, activo_id))

    def update(self, tenencia: Tenencia, **datos) -> Tenencia:
        for campo, valor in datos.items():
            setattr(tenencia, campo, valor)
        self.db.commit()
        self.db.refresh(tenencia)
        return tenencia

    def delete(self, tenencia: Tenencia) -> None:
        self.db.delete(tenencia)
        self.db.commit()
