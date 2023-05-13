from rich.traceback import install

from .environ import CONSOLE, create_env

# Create/assert folder structure
create_env()

# Rich console traceback hook
install(console=CONSOLE, indent_guides=True)
