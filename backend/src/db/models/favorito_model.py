from sqlalchemy import Column, ForeignKey, Integer

from src.db.connection import Base


class Favorito(Base):
    __tablename__ = "favoritos"

    inversor_id = Column(Integer, ForeignKey("inversores.id"), primary_key=True)
    activo_id = Column(Integer, ForeignKey("activos.id"), primary_key=True)
