from sqlalchemy import Boolean, Column, Integer, Numeric, String, true

from src.db.connection import Base


class Activo(Base):
    __tablename__ = "activos"

    id = Column(Integer, primary_key=True)
    ticker = Column(String(20), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(30), nullable=False)
    moneda = Column(String(3), nullable=False)
    precio_actual = Column(Numeric(24, 8), nullable=False)
    nivel_riesgo = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, server_default=true())
