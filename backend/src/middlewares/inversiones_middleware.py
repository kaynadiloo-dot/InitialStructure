from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


async def inversiones_integrity_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    codigo = getattr(exc.orig, "pgcode", None)
    if codigo == "23505":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": "Ya existe un registro con ese identificador o valor único."},
        )
    if codigo == "23503":
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": "La operación entra en conflicto con un registro relacionado."},
        )
    if codigo == "23514":
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "Los datos no cumplen una regla de validación de la base de datos."},
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "No se pudo guardar el cambio en la base de datos."},
    )
