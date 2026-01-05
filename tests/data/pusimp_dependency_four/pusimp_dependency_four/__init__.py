# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Mock dependency for pusimp tests.

This dependency raises an error on import to mimick the case of a broken package.
"""
raise RuntimeError("pusimp_dependency_four is a broken package.")
