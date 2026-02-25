"""
routers/task_router.py
----------------------
FastAPI APIRouter implementing all Task CRUD endpoints.

Prefix : /tasks
Tags   : ["Tasks"]

Endpoints
---------
POST   /tasks/              – Create a new task
GET    /tasks/              – List all tasks (filterable by status & priority)
GET    /tasks/{task_id}     – Retrieve a single task by ID
PUT    /tasks/{task_id}     – Full / partial update of a task
PATCH  /tasks/{task_id}/complete – Mark a task as completed
DELETE /tasks/{task_id}     – Delete a task
"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from database import get_db
from models.task import Task, TaskStatus, TaskPriority
from schemas.task_schema import TaskCreate, TaskUpdate, TaskOut, TaskComplete
from utils.response import success_response, not_found

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ─────────────────────────────────────────────────────────────────────────────
# POST /tasks/  –  Create a new task
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new task with the supplied data.

    - **title** is required.
    - **status** defaults to `todo`.
    - **priority** defaults to `medium`.
    """
    new_task = Task(
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return success_response(
        data=TaskOut.model_validate(new_task).model_dump(mode="json"),
        message="Task created successfully.",
        status_code=201,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /tasks/  –  List all tasks
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="List all tasks",
)
def list_tasks(
    status_filter: Optional[TaskStatus] = Query(
        default=None,
        alias="status",
        description="Filter by task status (todo | in_progress | done).",
    ),
    priority_filter: Optional[TaskPriority] = Query(
        default=None,
        alias="priority",
        description="Filter by priority (low | medium | high).",
    ),
    skip: int = Query(default=0, ge=0, description="Number of records to skip."),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return."),
    db: Session = Depends(get_db),
):
    """
    Return a paginated list of tasks, optionally filtered by **status**
    and/or **priority**.

    Query parameters:
    - `status`   – `todo` | `in_progress` | `done`
    - `priority` – `low` | `medium` | `high`
    - `skip`     – pagination offset (default 0)
    - `limit`    – page size (default 100, max 500)
    """
    query = db.query(Task)

    if status_filter is not None:
        query = query.filter(Task.status == status_filter)

    if priority_filter is not None:
        query = query.filter(Task.priority == priority_filter)

    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    total = query.count()

    return success_response(
        data={
            "total": total,
            "skip": skip,
            "limit": limit,
            "tasks": [
                TaskOut.model_validate(t).model_dump(mode="json") for t in tasks
            ],
        },
        message=f"{total} task(s) found.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /tasks/{task_id}  –  Get a single task
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/{task_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single task by its **ID**.

    Returns **404** if the task does not exist.
    """
    task = db.get(Task, task_id)
    if not task:
        not_found("Task")

    return success_response(
        data=TaskOut.model_validate(task).model_dump(mode="json"),
        message="Task retrieved successfully.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PUT /tasks/{task_id}  –  Update a task
# ─────────────────────────────────────────────────────────────────────────────

@router.put(
    "/{task_id}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
)
def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Session = Depends(get_db),
):
    """
    Update one or more fields on an existing task.

    Only fields included in the request body are updated
    (partial update behaviour even on a PUT endpoint).
    Returns **404** if the task does not exist.
    """
    task = db.get(Task, task_id)
    if not task:
        not_found("Task")

    # Apply only the fields that were explicitly provided
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Manually bump updated_at (SQLAlchemy onupdate fires on flush, not setattr)
    task.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    return success_response(
        data=TaskOut.model_validate(task).model_dump(mode="json"),
        message="Task updated successfully.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# PATCH /tasks/{task_id}/complete  –  Mark a task as completed
# ─────────────────────────────────────────────────────────────────────────────

@router.patch(
    "/{task_id}/complete",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Mark a task as completed",
)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Set `is_completed = True` and `status = done` on the specified task.

    Idempotent – calling this on an already-completed task is safe.
    Returns **404** if the task does not exist.
    """
    task = db.get(Task, task_id)
    if not task:
        not_found("Task")

    task.is_completed = True
    task.status = TaskStatus.DONE
    task.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    return success_response(
        data=TaskComplete.model_validate(task).model_dump(mode="json"),
        message="Task marked as completed.",
    )


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /tasks/{task_id}  –  Delete a task
# ─────────────────────────────────────────────────────────────────────────────

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a task",
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete a task by its **ID**.

    Returns **404** if the task does not exist.
    """
    task = db.get(Task, task_id)
    if not task:
        not_found("Task")

    db.delete(task)
    db.commit()

    return success_response(
        data={"deleted_id": task_id},
        message=f"Task {task_id} deleted successfully.",
    )
