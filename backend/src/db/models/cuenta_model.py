from sqlalchemy import Column, ForeignKey, Integer, Numeric, String, text

from src.db.connection import Base


class Cuenta(Base):
    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True)
    inversor_id = Column(Integer, ForeignKey("inversores.id"), nullable=False)
    numero_comitente = Column(String(40), nullable=False, unique=True)
    saldo_ars = Column(Numeric(24, 8), nullable=False, server_default=text("0"))
    saldo_usd = Column(Numeric(24, 8), nullable=False, server_default=text("0"))
