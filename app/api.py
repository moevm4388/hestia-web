from fastapi import APIRouter, Depends, Query, status
from fastapi.exceptions import HTTPException
from typing import Any

from hestia.common.exceptions import InvalidArgumentsError, UnknownIdentifierError
from hestia.common.module_group import ModuleGroup
from hestia.common.types import Identifier
from hestia.integer import IntegerModule
from hestia.natural import NaturalModule
from hestia.polynomial import PolynomialModule
from hestia.rational import RationalModule


def build_module_group() -> ModuleGroup:
    natural_module = NaturalModule()
    integer_module = IntegerModule(natural_module)
    rational_module = RationalModule(natural_module, integer_module)
    polynomial_module = PolynomialModule(
        natural_module, integer_module, rational_module
    )

    return ModuleGroup(
        natural_module,
        integer_module,
        rational_module,
        polynomial_module,
    )


router = APIRouter(tags=["API"])


@router.get("/functions", summary="Список доступных функций")
async def list_functions(
    module_group: ModuleGroup = Depends(build_module_group),
    as_indices: bool = False,
) -> list[str]:
    if as_indices:
        return list(map(lambda f: f.value, module_group.methods()))
    else:
        return list(map(lambda f: f.name, module_group.methods()))


@router.get("/call/{function}", summary="Вызов функции по имени или номеру")
async def call_function(
    function: Identifier | str,
    args: list[str] = Query([]),
    module_group: ModuleGroup = Depends(build_module_group),
) -> Any:
    try:
        identifier = Identifier.from_str(function)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неизвестная функция: '{function}'. См. `GET /functions` для получения списка функций",
        )

    try:
        result = module_group.call(identifier, args)
        return {"result": str(result)}
    except UnknownIdentifierError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Функция '{identifier}' не реализована",
        )
    except InvalidArgumentsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неверное количество аргументов (ожидалось {e.expected}, получено {e.actual})",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/health", summary="Проверка состояния сервиса")
async def health():
    return {"status": "All system operational"}
