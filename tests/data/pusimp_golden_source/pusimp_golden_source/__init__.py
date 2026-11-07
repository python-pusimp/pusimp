# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Golden source for pusimp.

The goal of this package is to provide a mock system path, a mock contact
URL, and a mock system package manager.
"""

import pathlib

contact_url = "mock contact URL"
system_path = str(pathlib.Path(__file__).parent.parent)
system_package_manager = "mock system package manager"


def pip_uninstall_call(
    executable: str, dependency_pypi_name: str, _dependency_actual_path: str
) -> str:
    """Report to the user how to uninstall a dependency with pip."""
    return f"{executable} -m pip uninstall {dependency_pypi_name}"
