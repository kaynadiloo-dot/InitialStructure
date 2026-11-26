from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func

from src.db.connection import Base


class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True)
    cuenta_id = Column(Integer, ForeignKey("cuentas.id"), nullable=False)
    tipo = Column(String(30), nullable=False)
    moneda = Column(String(3), nullable=False)
    monto = Column(Numeric(24, 8), nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    descripcion = Column(String(200), nullable=True)
