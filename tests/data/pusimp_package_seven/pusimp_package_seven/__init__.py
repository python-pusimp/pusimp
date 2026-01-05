# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Mock package for pusimp tests.

This is the same as pusimp_package_six, except for the fact that pusimp_dependency_four
is now a optional dependency. Therefore, even though it will always be raising an error, this package
will not raise an ImportError on import.
"""

import pusimp_golden_source

import pusimp

pusimp.prevent_user_site_imports(
    "pusimp_package_seven", pusimp_golden_source.system_package_manager, pusimp_golden_source.contact_url,
    pusimp_golden_source.system_path,
    ["pusimp_dependency_one", "pusimp_dependency_four"],
    ["pusimp-dependency-one", "pusimp-dependency-four"],
    [False, True],
    ["", ""],
    pusimp_golden_source.pip_uninstall_call
)

import pusimp_dependency_one  # noqa: E402, F401

try:
    import pusimp_dependency_missing  # noqa: F401
except ImportError:
    pass
