# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Test the snippet in README.md."""

import importlib
import os
import shutil
import sys
import tempfile

import pytest


def test_readme() -> None:
    """Test the snippet in README.md."""
    # Get snippets from file
    readme = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "README.md")
    assert os.path.exists(readme)
    with open(readme) as readme_file:
        num_backticks_lines = 0
        code_snippet = ""
        error_snippet = ""
        for line in readme_file.readlines():
            if line.startswith("```"):
                num_backticks_lines += 1
            else:
                if num_backticks_lines == 1:
                    code_snippet += line
                elif num_backticks_lines == 3:
                    error_snippet += line
        assert num_backticks_lines == 4
    code_snippet = code_snippet.strip("\n")
    error_snippet = error_snippet.strip("\n")
    # Generate mock site paths
    readme_system_site_path = "/usr/lib/python3.xy/site-packages"
    readme_user_site_path = "~/.local/lib/python3.xy/site-packages"
    mock_executable_path = "python3"
    mock_system_site_path = tempfile.mkdtemp()
    mock_user_site_path = tempfile.mkdtemp()
    sys.path.insert(0, mock_user_site_path)
    sys.path.insert(1, mock_system_site_path)
    # Write package and dependencies to disk
    packages_code = {
        "my_package": code_snippet.replace(readme_system_site_path, mock_system_site_path),
        # "my_dependency_one": "",  # purposely missing
        "my_dependency_two": "raise RuntimeError('purposely broken')",
        "my_dependency_three": "",
        "my_dependency_four": ""
    }
    for (package_import_name, package_code) in packages_code.items():
        for mock_site_path in (mock_user_site_path, mock_system_site_path):
            package_user_site = os.path.join(mock_site_path, package_import_name)
            os.makedirs(package_user_site)
            with open(os.path.join(package_user_site, "__init__.py"), "w") as init_file:
                init_file.write(package_code)
    shutil.rmtree(os.path.join(mock_user_site_path, "my_dependency_one"), ignore_errors=True)
    try:
        with pytest.raises(ImportError) as excinfo:
            importlib.import_module("my_package")
        import_error_text = str(excinfo.value)
        import_error_text = import_error_text.replace(f"{sys.executable} -m", f"{mock_executable_path} -m")
        import_error_text = import_error_text.replace(mock_system_site_path, readme_system_site_path)
        import_error_text = import_error_text.replace(mock_user_site_path, readme_user_site_path)
        import_error_text = "\n".join([line.rstrip() for line in import_error_text.splitlines()])
        print(f"The following ImportError was raised:\n{import_error_text}")
    finally:
        del sys.path[0]
        del sys.path[1]
        shutil.rmtree(mock_user_site_path, ignore_errors=True)
        shutil.rmtree(mock_system_site_path, ignore_errors=True)
    # Check that the README is up to date with the current error message
    assert error_snippet == import_error_text
