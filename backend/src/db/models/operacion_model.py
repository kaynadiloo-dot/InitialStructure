from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func

from src.db.connection import Base


class Operacion(Base):
    __tablename__ = "operaciones"

    id = Column(Integer, primary_key=True)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=False)
    activo_id = Column(Integer, ForeignKey("activos.id"), nullable=False)
    tipo = Column(String(30), nullable=False)
    cantidad = Column(Numeric(24, 8), nullable=False)
    precio_unitario = Column(Numeric(24, 8), nullable=False)
    comision = Column(Numeric(24, 8), nullable=False)
    total = Column(Numeric(24, 8), nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    estado = Column(String(30), nullable=False)
    ganancia_realizada = Column(Numeric(32, 8), nullable=True)
