from decimal import Decimal
from typing import Annotated

from pydantic import Field, StringConstraints


IdPositivo = Annotated[int, Field(gt=0)]
Cuit = Annotated[str, StringConstraints(pattern=r"^[0-9]{11}$")]
DecimalMonetario = Annotated[Decimal, Field(max_digits=24, decimal_places=8)]
