"""
Set up or assert the presence of the proper folder structure.
"""

from .environ import create_env

__all__: list[str] = ["create_env"]

create_env()
