from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.db import Base


class Task(Base):
    __tablename__ = "tasks"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    status = Column(String, default="created", nullable=False)

    def __repr__(self):
        return f"<Task(uuid={self.uuid}, title='{self.title}', status='{self.status}')>"
