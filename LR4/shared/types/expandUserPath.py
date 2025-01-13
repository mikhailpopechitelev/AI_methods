from pathlib import Path
from pydantic import AfterValidator

from annotated_types import Annotated

ExpandUserPath = Annotated[Path, AfterValidator(lambda p: p.expanduser())]
