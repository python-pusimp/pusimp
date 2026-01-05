# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Mock package for pusimp tests.

This is the same as pusimp_package_eight, except for the fact that pusimp.prevent_user_site_imports is
called before the imports of pusimp_dependency_five and pusimp_dependency_six.
"""

import pusimp_golden_source

import pusimp

pusimp.prevent_user_site_imports(
    "pusimp_package_nine", pusimp_golden_source.system_package_manager, pusimp_golden_source.contact_url,
    pusimp_golden_source.system_path,
    ["pusimp_dependency_five", "pusimp_dependency_six"],
    ["pusimp-dependency-five", "pusimp-dependency-six"],
    [False, True],
    ["pusimp_dependency_five is mandatory.", "pusimp_dependency_six is optional."],
    pusimp_golden_source.pip_uninstall_call
)

import pusimp_dependency_five  # noqa: E402, F401

try:
    import pusimp_dependency_six  # noqa: F401
except ImportError:
    pass
