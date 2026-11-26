from sqlalchemy import Column, ForeignKey, Integer, Numeric

from src.db.connection import Base


class Tenencia(Base):
    __tablename__ = "tenencias"

    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), primary_key=True)
    activo_id = Column(Integer, ForeignKey("activos.id"), primary_key=True)
    cantidad = Column(Numeric(24, 8), nullable=False)
    precio_promedio = Column(Numeric(24, 8), nullable=False)
