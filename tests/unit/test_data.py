# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Test imports of mock packages in tests/data."""

import importlib
import os
import shutil
import sys
import tempfile

import pytest

import pusimp_golden_source  # isort: skip


all_mock_packages = [
    "pusimp_package_one",
    "pusimp_package_two",
    "pusimp_package_three",
    "pusimp_package_four",
    "pusimp_package_five",
    "pusimp_package_six",
    "pusimp_package_seven",
    "pusimp_package_eight",
    "pusimp_package_nine"
]

all_mock_dependencies = [
    "pusimp_dependency_one",
    "pusimp_dependency_two",
    "pusimp_dependency_three",
    "pusimp_dependency_four",
    "pusimp_dependency_five",
    "pusimp_dependency_six"
]

all_mock_golden = [
    "pusimp_golden_source"
]


def test_data_versions() -> None:
    """Test that the version of every mock package, dependency and golden is the same as the main package."""
    pusimp_version = importlib.metadata.version("pusimp")
    if "9999" in pusimp_version:
        # Versions on TestPyPI have a mock version number formed by the actual version number, a separator 9999,
        # and then the upload date to work around the fact that releases cannot be overwritten. Recognize this
        # case and transform the mock version number into the actual version number.
        pusimp_version, _ = pusimp_version.split("9999")
        if pusimp_version[-1] == ".":
            # Leading zeros are not conserved when preparing the distribution: just add it back.
            pusimp_version = f"{pusimp_version}0"
    for mock in all_mock_packages + all_mock_dependencies + all_mock_golden:
        assert importlib.metadata.version(mock.replace("_", "-")) == pusimp_version


def test_data_one() -> None:
    """Test that the first mock package in tests/data import correctly."""
    import pusimp_package_one  # noqa: F401


def test_data_two() -> None:
    """Test that the second mock package in tests/data import correctly."""
    import pusimp_package_two  # noqa: F401


def test_data_three() -> None:
    """Test that the third mock package in tests/data import correctly."""
    import pusimp_package_three  # noqa: F401


def test_data_four() -> None:
    """Test that the fourth mock package in tests/data fails to import due to a missing mandatory dependency."""
    with pytest.raises(ImportError) as excinfo:
        import pusimp_package_four  # noqa: F401
    import_error_text = str(excinfo.value)
    print(f"The following ImportError was raised:\n{import_error_text}")
    assert "pusimp has detected the following problems with pusimp_package_four dependencies" in import_error_text
    assert "Missing dependencies:" in import_error_text
    assert (
        "* pusimp_dependency_missing is missing. Its expected path was "
        f"{os.path.join(pusimp_golden_source.system_path, 'pusimp_dependency_missing', '__init__.py')}."
    ) in import_error_text
    assert "To install missing dependencies:" in import_error_text
    assert "* check how to install pusimp_dependency_missing with mock system package manager" in import_error_text
    assert "believe that this message appears incorrectly, report this at mock contact URL ." in import_error_text


def test_data_five() -> None:
    """Test that the fifth mock package in tests/data import correctly, because the missing dependency is optional."""
    import pusimp_package_five  # noqa: F401


def test_data_six() -> None:
    """Test that the sixth mock package in tests/data fails to import due to a broken mandatory dependency."""
    with pytest.raises(ImportError) as excinfo:
        import pusimp_package_six  # noqa: F401
    import_error_text = str(excinfo.value)
    print(f"The following ImportError was raised:\n{import_error_text}")
    assert "pusimp has detected the following problems with pusimp_package_six dependencies" in import_error_text
    assert "Broken dependencies:" in import_error_text
    assert (
        "pusimp_dependency_four is broken. Error on import was 'pusimp_dependency_four is a broken package.'."
    ) in import_error_text
    assert "To fix broken dependencies:" in import_error_text
    assert (
        f"* run '{sys.executable} -m pip show pusimp-dependency-four' in a terminal: if the location field is not "
        f"{pusimp_golden_source.system_path} consider running '{sys.executable} -m pip uninstall "
        "pusimp-dependency-four' in a terminal, because the broken dependency is probably being imported from "
        "a local path rather than from the path provided by mock system package manager."
    ) in import_error_text
    assert "believe that this message appears incorrectly, report this at mock contact URL ." in import_error_text


def test_data_seven() -> None:
    """Test that the seventh mock package in tests/data import correctly, because the broken dependency is optional."""
    import pusimp_package_seven  # noqa: F401


def test_data_eight_nine_ten() -> None:
    """Test that the eighth to tenth mock package in tests/data fails to import due to dependencies from user site.

    Note that the eighth and ninth mock package are tested in the same function, rather than two separate functions,
    because they both the depend on pusimp_dependency_five and pusimp_dependency_six, which will get replaced
    by an user-site installation inside this test. However, since the python interpreter only loads a module once,
    we have to be sure that every mock package that requires pusimp_dependency_five and pusimp_dependency_six operates
    in the same environment.
    """
    mock_system_site_path = pusimp_golden_source.system_path
    mock_user_site_path = tempfile.mkdtemp()
    sys.path.insert(0, mock_user_site_path)
    for dependency_import_name in ("pusimp_dependency_five", "pusimp_dependency_six"):
        dependency_user_site = os.path.join(mock_user_site_path, dependency_import_name)
        os.makedirs(dependency_user_site)
        with open(os.path.join(dependency_user_site, "__init__.py"), "w") as init_file:
            init_file.write("# created by pytest")
    try:
        for pusimp_package in ("pusimp_package_eight", "pusimp_package_nine", "pusimp_package_ten"):
            with pytest.raises(ImportError) as excinfo:
                importlib.import_module(pusimp_package)
            import_error_text = str(excinfo.value)
            print(f"The following ImportError was raised:\n{import_error_text}")
            assert (
                f"pusimp has detected the following problems with {pusimp_package} dependencies"
            ) in import_error_text
            if pusimp_package == "pusimp_package_ten":
                assert "Missing dependencies:" in import_error_text
                assert "To install missing dependencies:" in import_error_text
                assert "Broken dependencies:" in import_error_text
                assert "To fix broken dependencies:" in import_error_text
            assert (
                "Dependencies imported from a local path rather than from the path provided by "
                "mock system package manager:"
            ) in import_error_text
            assert "To uninstall local dependencies:" in import_error_text
            if pusimp_package == "pusimp_package_ten":
                assert (
                    "* pusimp_dependency_missing is missing. Its expected path was "
                    f"{os.path.join(mock_system_site_path, 'pusimp_dependency_missing', '__init__.py')}."
                ) in import_error_text
                assert (
                    "* check how to install pusimp_dependency_missing with mock system package manager."
                ) in import_error_text
                assert (
                    "pusimp_dependency_four is broken. Error on import was "
                    "'pusimp_dependency_four is a broken package.'."
                ) in import_error_text
                assert (
                    f"* run '{sys.executable} -m pip show pusimp-dependency-four' in a terminal: if the location "
                    f"field is not {mock_system_site_path} consider running '{sys.executable} -m pip uninstall "
                    "pusimp-dependency-four' in a terminal, because the broken dependency is probably being imported "
                    "from a local path rather than from the path provided by mock system package manager."
                ) in import_error_text
            for (dependency_import_name, dependency_optional_string) in (
                ("pusimp_dependency_five", "mandatory"),
                ("pusimp_dependency_six", "optional")
            ):
                assert (
                    f"* {dependency_import_name} was imported from a local path: expected in "
                    f"{os.path.join(mock_system_site_path, dependency_import_name, '__init__.py')}, "
                    f"but imported from "
                    f"{os.path.join(mock_user_site_path, dependency_import_name, '__init__.py')}."
                ) in import_error_text
                dependency_pypi_name = dependency_import_name.replace("_", "-")
                assert (
                    f"* run '{sys.executable} -m pip uninstall {dependency_pypi_name}' in a terminal, "
                    f"and verify that you are prompted to confirm removal of files in "
                    f"{os.path.join(mock_user_site_path, dependency_import_name)}. "
                    f"{dependency_import_name} is {dependency_optional_string}."
                ) in import_error_text
            assert (
                "believe that this message appears incorrectly, report this at mock contact URL ."
            ) in import_error_text
    finally:
        del sys.path[0]
        shutil.rmtree(mock_user_site_path, ignore_errors=True)
