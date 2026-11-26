from sqlalchemy import Column, DateTime, Integer, String, func

from src.db.connection import Base


class Inversor(Base):
    __tablename__ = "inversores"

    id = Column(Integer, primary_key=True)
    email = Column(String(254), nullable=False, unique=True)
    nombre = Column(String(100), nullable=False)
    cuit = Column(String(11), nullable=False, unique=True)
    perfil_riesgo = Column(String(30), nullable=False)
    fecha_alta = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
