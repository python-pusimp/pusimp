# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Mock package for pusimp tests.

This package imports pusimp_dependency_one and pusimp_dependency_two.
pusimp_dependency_two will sometimes be broken by user-site imports.
"""

import pusimp_dependency_one  # noqa: F401
import pusimp_dependency_two  # noqa: F401
import pusimp_golden_source

import pusimp

pusimp.prevent_user_site_imports(
    "pusimp_package_one", pusimp_golden_source.system_package_manager, pusimp_golden_source.contact_url,
    pusimp_golden_source.system_path,
    ["pusimp_dependency_one", "pusimp_dependency_two"],
    ["pusimp-dependency-one", "pusimp-dependency-two"],
    [False, False],
    ["", "pusimp_dependency_two is mandatory."],
    pusimp_golden_source.pip_uninstall_call
)
