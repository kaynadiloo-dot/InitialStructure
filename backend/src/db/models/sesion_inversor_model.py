from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from src.db.connection import Base


class SesionInversor(Base):
    __tablename__ = "sesiones_inversores"

    token_hash = Column(String(64), primary_key=True)
    inversor_id = Column(Integer, ForeignKey("inversores.id", ondelete="CASCADE"), nullable=False, index=True)
    vence = Column(DateTime(timezone=True), nullable=False, index=True)
