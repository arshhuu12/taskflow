"""
models/task.py
--------------
SQLAlchemy ORM model for the Task entity.
Maps to the `tasks` table in the database.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Enum,
    Boolean,
    DateTime,
)
from database import Base


# ── Enums ─────────────────────────────────────────────────────────────────────

class TaskStatus(str, enum.Enum):
    """Lifecycle status of a task."""
    TODO        = "todo"
    IN_PROGRESS = "in_progress"
    DONE        = "done"


class TaskPriority(str, enum.Enum):
    """Urgency level of a task."""
    LOW    = "low"
    MEDIUM = "medium"
    HIGH   = "high"


# ── ORM Model ─────────────────────────────────────────────────────────────────

class Task(Base):
    """
    Represents a single actionable task in the system.

    Columns:
        id          – Auto-incrementing primary key.
        title       – Short, required name of the task (max 255 chars).
        description – Optional longer description of the task.
        status      – Current lifecycle state (todo / in_progress / done).
        priority    – Urgency level (low / medium / high).
        is_completed– Convenience boolean; set to True by the /complete endpoint.
        due_date    – Optional deadline (stored as UTC datetime).
        created_at  – Timestamp of record creation (auto-set, UTC).
        updated_at  – Timestamp of last modification (auto-updated, UTC).
    """

    __tablename__ = "tasks"

    id: int = Column(Integer, primary_key=True, index=True)

    title: str = Column(String(255), nullable=False)
    description: str | None = Column(Text, nullable=True)

    status: TaskStatus = Column(
        Enum(TaskStatus),
        default=TaskStatus.TODO,
        nullable=False,
    )
    priority: TaskPriority = Column(
        Enum(TaskPriority),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )

    is_completed: bool = Column(Boolean, default=False, nullable=False)

    due_date: datetime | None = Column(DateTime(timezone=True), nullable=True)

    created_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: datetime = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id!r} title={self.title!r} status={self.status!r}>"
