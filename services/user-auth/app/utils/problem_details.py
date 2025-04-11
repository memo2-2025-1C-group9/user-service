from fastapi.responses import JSONResponse


def problem_detail_response(
    status_code: int,
    title: str,
    detail: str,
    type: str = "about:blank",
    instance: str = "",
):
    return JSONResponse(
        status_code=status_code,
        content={
            "type": type,
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": instance,
        },
        media_type="application/problem+json",
    )
