"""
utils/response.py
-----------------
Standardised JSON response helpers used by all route handlers.

Every API response from TaskFlow is wrapped in a consistent envelope:

    Success:
        {
            "success": true,
            "message": "...",
            "data": <payload>
        }

    Error:
        raised as HTTPException; FastAPI serialises this automatically:
        {
            "detail": "..."
        }
"""

from typing import Any
from fastapi import HTTPException


def success_response(
    data: Any,
    message: str = "Success",
    status_code: int = 200,
) -> dict:
    """
    Build a standardised success envelope.

    Args:
        data:        The payload to include under the "data" key.
        message:     Human-readable summary of the operation.
        status_code: HTTP status code (informational; not enforced here –
                     the router's `status_code` param controls the actual code).

    Returns:
        A dict ready to be returned from a FastAPI route.
    """
    return {
        "success": True,
        "message": message,
        "data": data,
    }


def error_response(message: str, status_code: int = 400) -> None:
    """
    Raise an HTTPException with a descriptive error detail.

    Args:
        message:     Human-readable error description.
        status_code: HTTP status code (e.g. 400, 422, 500).

    Raises:
        HTTPException: FastAPI catches this and returns a JSON error body.
    """
    raise HTTPException(status_code=status_code, detail=message)


def not_found(resource: str = "Item") -> None:
    """
    Convenience wrapper for 404 errors.

    Args:
        resource: Name of the missing resource, e.g. "Task".

    Raises:
        HTTPException: 404 with "<resource> not found."
    """
    error_response(f"{resource} not found.", status_code=404)
