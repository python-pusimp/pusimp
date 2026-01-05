# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Mock package for pusimp tests.

This package imports pusimp_dependency_five and pusimp_dependency_six.
pusimp_dependency_five is a mandatory dependency, while pusimp_dependency_six is an optional dependency.
Both dependencies will always be marked as imported from a user site.

The main difference compared to pusimp_package_two and pusimp_package_three is that their dependencies
there will sometimes be imported from a user site, while here the dependencies are always imported from a user site.
"""

import pusimp_dependency_five  # noqa: F401
import pusimp_golden_source

try:
    import pusimp_dependency_six  # noqa: F401
except ImportError:
    pass

import pusimp

pusimp.prevent_user_site_imports(
    "pusimp_package_eight", pusimp_golden_source.system_package_manager, pusimp_golden_source.contact_url,
    pusimp_golden_source.system_path,
    ["pusimp_dependency_five", "pusimp_dependency_six"],
    ["pusimp-dependency-five", "pusimp-dependency-six"],
    [False, True],
    ["pusimp_dependency_five is mandatory.", "pusimp_dependency_six is optional."],
    pusimp_golden_source.pip_uninstall_call
)
