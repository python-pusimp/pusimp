# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Mock package for pusimp tests.

This package imports:
* pusimp_dependency_four, a mandatory dependency which will always be broken,
* pusimp_dependency_five, a mandatory dependency, and which will always be marked as imported from a user site,
* pusimp_dependency_six, an optional dependency, and which will always be marked as imported from a user site,
* pusimp_dependency_missing, a mandatory dependency which will always be missing.
"""

import pusimp_golden_source

import pusimp

pusimp.prevent_user_site_imports(
    "pusimp_package_ten", pusimp_golden_source.system_package_manager, pusimp_golden_source.contact_url,
    pusimp_golden_source.system_path,
    ["pusimp_dependency_four", "pusimp_dependency_five", "pusimp_dependency_six", "pusimp_dependency_missing"],
    ["pusimp-dependency-four", "pusimp-dependency-five", "pusimp-dependency-six", "pusimp-dependency-missing"],
    [False, False, True, False],
    ["", "pusimp_dependency_five is mandatory.", "pusimp_dependency_six is optional.", ""],
    pusimp_golden_source.pip_uninstall_call
)

import pusimp_dependency_five  # noqa: E402, F401
import pusimp_dependency_four  # noqa: E402, F401
import pusimp_dependency_missing  # noqa: E402, F401

try:
    import pusimp_dependency_six  # noqa: F401
except ImportError:
    pass
