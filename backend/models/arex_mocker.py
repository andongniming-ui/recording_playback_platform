from sqlalchemy import Column, Integer, String, Boolean, Text, BigInteger
from database import Base


class ArexMocker(Base):
    """Raw mocker data uploaded by the AREX Java agent.

    One row per mocker (Servlet entry-point OR sub-call).
    Multiple rows share the same record_id when a single transaction
    produces a Servlet mocker plus DB/HTTP sub-call mockers.
    """
    __tablename__ = "arex_mocker"

    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(String(128), index=True, nullable=False)
    app_id = Column(String(128), index=True, nullable=False)
    category_name = Column(String(64), nullable=True)
    is_entry_point = Column(Boolean, default=False, nullable=False)
    mocker_data = Column(Text, nullable=False)   # full mocker JSON
    created_at_ms = Column(BigInteger, nullable=True, index=True)  # epoch ms from agent
