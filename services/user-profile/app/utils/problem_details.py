from fastapi.responses import JSONResponse
from typing import Dict, Optional


def problem_detail_response(
    status_code: int,
    title: str,
    detail: str,
    type: str = "about:blank",
    instance: str = "",
    headers: Optional[Dict[str, str]] = None,
):
    """
    Crea una respuesta de error en formato RFC 7807 Problem Details.

    Este formato es el estándar para APIs REST.
    """
    content = {
        "type": type,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
    }

    return JSONResponse(
        status_code=status_code,
        content=content,
        headers=headers,
        media_type="application/problem+json",
    )
