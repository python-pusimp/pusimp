# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Mock package for pusimp tests.

This package imports pusimp_dependency_one, pusimp_dependency_two and pusimp_dependency_three.
pusimp_dependency_two will sometimes be broken by user-site imports, and is a mandatory dependency.
pusimp_dependency_three will sometimes be broken by user-site imports, and is an optional dependency.
"""

import pusimp_dependency_one  # noqa: F401
import pusimp_dependency_two  # noqa: F401
import pusimp_golden_source

try:
    import pusimp_dependency_three  # noqa: F401
except ImportError:
    pass

import pusimp

pusimp.prevent_user_site_imports(
    "pusimp_package_two", pusimp_golden_source.system_package_manager, pusimp_golden_source.contact_url,
    pusimp_golden_source.system_path,
    ["pusimp_dependency_one", "pusimp_dependency_two", "pusimp_dependency_three"],
    ["pusimp-dependency-one", "pusimp-dependency-two", "pusimp-dependency-three"],
    [False, False, True],
    ["", "pusimp_dependency_two is mandatory.", "pusimp_dependency_three is optional."],
    pusimp_golden_source.pip_uninstall_call
)
