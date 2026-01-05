# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Mock package for pusimp tests.

This package imports pusimp_dependency_one and pusimp_dependency_missing.
pusimp_dependency_missing is a mandatory dependency and will always be missing, and therefore
this package will raise an ImportError on import.
"""

import pusimp_golden_source

import pusimp

pusimp.prevent_user_site_imports(
    "pusimp_package_four", pusimp_golden_source.system_package_manager, pusimp_golden_source.contact_url,
    pusimp_golden_source.system_path,
    ["pusimp_dependency_one", "pusimp_dependency_missing"],
    ["pusimp-dependency-one", "pusimp-dependency-missing"],
    [False, False],
    ["", ""],
    pusimp_golden_source.pip_uninstall_call
)

import pusimp_dependency_missing  # noqa: E402, F401
import pusimp_dependency_one  # noqa: E402, F401
