from fastapi import Depends, FastAPI

from hestia.integer import IntegerModule
from hestia.natural import NaturalModule
from hestia.rational import RationalModule
from hestia.polynomial import PolynomialModule
from hestia.common.module_group import ModuleGroup


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


app = FastAPI()


@app.get("/functions")
async def get_function_indices(
    module_group: ModuleGroup = Depends(build_module_group),
    as_indices: bool = False,
) -> list[str]:
    if as_indices:
        return list(map(lambda f: f.value, module_group.methods()))
    else:
        return list(map(lambda f: f.name, module_group.methods()))
