# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Test imports of mock packages in tests/data."""

import importlib.metadata
import pathlib
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
    "pusimp_package_nine",
]

all_mock_dependencies = [
    "pusimp_dependency_one",
    "pusimp_dependency_two",
    "pusimp_dependency_three",
    "pusimp_dependency_four",
    "pusimp_dependency_five",
    "pusimp_dependency_six",
]

all_mock_golden = ["pusimp_golden_source"]


def test_data_versions() -> None:
    """Test that all mock package versions match the main package."""
    pusimp_version = importlib.metadata.version("pusimp")
    if "9999" in pusimp_version:
        # TestPyPI versions include separator 9999 and an upload date
        # because releases cannot be overwritten. Convert to the actual
        # version number for comparison.
        pusimp_version, _ = pusimp_version.split("9999")
        if pusimp_version[-1] == ".":
            # Restore the trailing zero lost when preparing distributions.
            pusimp_version = f"{pusimp_version}0"
    for mock in all_mock_packages + all_mock_dependencies + all_mock_golden:
        assert (
            importlib.metadata.version(mock.replace("_", "-")) == pusimp_version
        )


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
    """Test failure with a missing mandatory dependency."""
    with pytest.raises(ImportError) as excinfo:
        import pusimp_package_four  # noqa: F401
    import_error_text = str(excinfo.value)
    assert (
        "pusimp has detected the following problems with "
        "pusimp_package_four dependencies" in import_error_text
    )
    assert "Missing dependencies:" in import_error_text
    missing_dependency_path = (
        pathlib.Path(pusimp_golden_source.system_path)
        / "pusimp_dependency_missing"
        / "__init__.py"
    )
    assert (
        "* pusimp_dependency_missing is missing. "
        "Its expected path was "
        f"{missing_dependency_path}."
    ) in import_error_text
    assert "To install missing dependencies:" in import_error_text
    assert (
        "* check how to install pusimp_dependency_missing "
        "with mock system package manager" in import_error_text
    )
    assert (
        "believe that this message appears incorrectly, report this "
        "at mock contact URL ." in import_error_text
    )


def test_data_five() -> None:
    """Test import success with an optional missing dependency."""
    import pusimp_package_five  # noqa: F401


def test_data_six() -> None:
    """Test failure with a broken mandatory dependency."""
    with pytest.raises(ImportError) as excinfo:
        import pusimp_package_six  # noqa: F401
    import_error_text = str(excinfo.value)
    assert (
        "pusimp has detected the following problems with "
        "pusimp_package_six dependencies" in import_error_text
    )
    assert "Broken dependencies:" in import_error_text
    assert (
        "pusimp_dependency_four is broken. Error on import was "
        "'pusimp_dependency_four is a broken package.'."
    ) in import_error_text
    assert "To fix broken dependencies:" in import_error_text
    assert (
        f"* run '{sys.executable} -m pip show pusimp-dependency-four' "
        "in a terminal: if the location field is not "
        f"{pusimp_golden_source.system_path} consider running "
        f"'{sys.executable} -m pip uninstall pusimp-dependency-four' "
        "in a terminal, because the broken dependency is probably being "
        "imported from a local path rather than from the path provided by "
        "mock system package manager."
    ) in import_error_text
    assert (
        "believe that this message appears incorrectly, report this "
        "at mock contact URL ." in import_error_text
    )


def test_data_seven() -> None:
    """Test import success with an optional broken dependency."""
    import pusimp_package_seven  # noqa: F401


def test_data_eight_nine_ten() -> None:
    """Test that packages eight to ten reject dependencies from user-site.

    Packages eight and nine share dependencies that are replaced by
    user-site installations below. Since Python loads each module only once,
    test all affected packages in the same environment.
    """
    mock_system_site_path = pusimp_golden_source.system_path
    mock_user_site_path = tempfile.mkdtemp()
    sys.path.insert(0, mock_user_site_path)
    for dependency_import_name in (
        "pusimp_dependency_five",
        "pusimp_dependency_six",
    ):
        dependency_user_site = (
            pathlib.Path(mock_user_site_path) / dependency_import_name
        )
        dependency_user_site.mkdir()
        with (dependency_user_site / "__init__.py").open("w") as init_file:
            init_file.write("# created by pytest")
    try:
        for pusimp_package in (
            "pusimp_package_eight",
            "pusimp_package_nine",
            "pusimp_package_ten",
        ):
            with pytest.raises(ImportError) as excinfo:
                importlib.import_module(pusimp_package)
            import_error_text = str(excinfo.value)
            assert (
                "pusimp has detected the following problems with "
                f"{pusimp_package} dependencies"
            ) in import_error_text
            if pusimp_package == "pusimp_package_ten":
                assert "Missing dependencies:" in import_error_text
                assert "To install missing dependencies:" in import_error_text
                assert "Broken dependencies:" in import_error_text
                assert "To fix broken dependencies:" in import_error_text
            assert (
                "Dependencies imported from a local path rather than from "
                "the path provided by "
                "mock system package manager:"
            ) in import_error_text
            assert "To uninstall local dependencies:" in import_error_text
            if pusimp_package == "pusimp_package_ten":
                missing_dependency_path = (
                    pathlib.Path(mock_system_site_path)
                    / "pusimp_dependency_missing"
                    / "__init__.py"
                )
                assert (
                    "* pusimp_dependency_missing is missing. "
                    "Its expected path was "
                    f"{missing_dependency_path}."
                ) in import_error_text
                assert (
                    "* check how to install pusimp_dependency_missing "
                    "with mock system package manager."
                ) in import_error_text
                assert (
                    "pusimp_dependency_four is broken. Error on import was "
                    "'pusimp_dependency_four is a broken package.'."
                ) in import_error_text
                assert (
                    f"* run '{sys.executable} -m pip show "
                    "pusimp-dependency-four' "
                    "in a terminal: if the location field is not "
                    f"{mock_system_site_path} consider running "
                    f"'{sys.executable} -m pip uninstall "
                    "pusimp-dependency-four' "
                    "in a terminal, because the broken dependency is probably "
                    "being imported from a local path rather than from the "
                    "path provided by mock system package manager."
                ) in import_error_text
            for dependency_import_name, dependency_optional_string in (
                ("pusimp_dependency_five", "mandatory"),
                ("pusimp_dependency_six", "optional"),
            ):
                system_dependency_path = (
                    pathlib.Path(mock_system_site_path)
                    / dependency_import_name
                    / "__init__.py"
                )
                user_dependency_path = (
                    pathlib.Path(mock_user_site_path)
                    / dependency_import_name
                    / "__init__.py"
                )
                assert (
                    f"* {dependency_import_name} was imported from a local "
                    "path: expected in "
                    f"{system_dependency_path}, "
                    f"but imported from "
                    f"{user_dependency_path}."
                ) in import_error_text
                dependency_pypi_name = dependency_import_name.replace("_", "-")
                user_dependency_dir = (
                    pathlib.Path(mock_user_site_path) / dependency_import_name
                )
                assert (
                    f"* run '{sys.executable} -m pip uninstall "
                    f"{dependency_pypi_name}' in a terminal, and verify "
                    "that you are prompted to confirm removal of files in "
                    f"{user_dependency_dir}. "
                    f"{dependency_import_name} is {dependency_optional_string}."
                ) in import_error_text
            assert (
                "believe that this message appears incorrectly, report this "
                "at mock contact URL ."
            ) in import_error_text
    finally:
        del sys.path[0]
        shutil.rmtree(mock_user_site_path, ignore_errors=True)
