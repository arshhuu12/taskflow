"""
schemas/task_schema.py
----------------------
Pydantic v2 schemas for Task request validation and response serialisation.

Schema hierarchy:
    TaskBase      – shared, optional fields used for updates
    TaskCreate    – stricter variant of TaskBase for creation (title required)
    TaskUpdate    – all fields optional; for PUT /tasks/{id}
    TaskComplete  – thin schema returned by the /complete endpoint
    TaskOut       – full response schema (includes DB-generated fields)
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from models.task import TaskStatus, TaskPriority


# ── Base (shared field definitions) ──────────────────────────────────────────

class TaskBase(BaseModel):
    title: Optional[str] = Field(
        default=None,
        max_length=255,
        examples=["Buy groceries"],
        description="Short name of the task.",
    )
    description: Optional[str] = Field(
        default=None,
        examples=["Milk, eggs, bread"],
        description="Detailed description of what needs to be done.",
    )
    status: Optional[TaskStatus] = Field(
        default=None,
        examples=[TaskStatus.TODO],
        description="Current lifecycle status.",
    )
    priority: Optional[TaskPriority] = Field(
        default=None,
        examples=[TaskPriority.MEDIUM],
        description="Urgency level of the task.",
    )
    due_date: Optional[datetime] = Field(
        default=None,
        examples=["2025-12-31T23:59:00Z"],
        description="Optional deadline (ISO-8601 UTC datetime).",
    )


# ── Create ───────────────────────────────────────────────────────────────────

class TaskCreate(TaskBase):
    """
    Body schema for POST /tasks/.
    title is required; all other fields default to sensible values.
    """
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["Deploy to production"],
        description="Required short name of the task.",
    )
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)


# ── Update ───────────────────────────────────────────────────────────────────

class TaskUpdate(TaskBase):
    """
    Body schema for PUT /tasks/{id}.
    Every field is optional – only supplied fields are updated.
    """
    pass  # All fields are already Optional in TaskBase


# ── Output (Response) ────────────────────────────────────────────────────────

class TaskOut(BaseModel):
    """
    Full response schema returned by all endpoints.
    Includes DB-generated fields (id, timestamps, is_completed).
    """
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    is_completed: bool
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Enable ORM mode so Pydantic can read SQLAlchemy model attributes
    model_config = ConfigDict(from_attributes=True)


# ── Convenience ── ────────────────────────────────────────────────────────────

class TaskComplete(BaseModel):
    """Minimal response returned by PATCH /tasks/{id}/complete."""
    id: int
    is_completed: bool
    status: TaskStatus
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
