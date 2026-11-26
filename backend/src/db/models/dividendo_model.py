from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric

from src.db.connection import Base


class Dividendo(Base):
    __tablename__ = "dividendos"

    id = Column(Integer, primary_key=True)
    activo_id = Column(Integer, ForeignKey("activos.id"), nullable=False)
    monto_por_unidad = Column(Numeric(24, 8), nullable=False)
    fecha_pago = Column(Date, nullable=False)
