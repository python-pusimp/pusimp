# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Prevent user-site imports on a specific set of dependencies."""

import importlib
import os
import sys
import typing


def prevent_user_site_imports(
    package_name: str,
    system_manager: str,
    contact_url: str,
    dependencies_expected_prefix: str,
    dependencies_import_name: list[str],
    dependencies_pypi_name: list[str],
    dependencies_optional: list[bool],
    dependencies_extra_error_message: list[str],
    pip_uninstall_call: typing.Callable[[str, str, str], str]
) -> None:
    """
    Prevent user-site imports on a specific set of dependencies.

    Parameters
    ----------
    package_name
        The name of the package which dependencies must be guarded against user-site imports.
        This information is only employed to prepare the text of error messages.
    system_manager
        The name of the system manager with which the package was installed.
        This information is only employed to prepare the text of error messages.
    contact_url
        The contact URL for the package development.
        This information is only employed to prepare the text of error messages.
    dependencies_expected_prefix
        The expected prefix of import locations managed by the system manager.
        This information is employed while determining the import location of each dependency
        and to prepare the text of error messages.
    dependencies_import_name
        The import name of the dependencies of the package.
        This information is employed while determining the import location of each dependency
        and to prepare the text of error messages.
    dependencies_pypi_name
        The pypi name of the dependencies of the package.
        This information is only employed to prepare the text of error messages.
    dependencies_optional
        A list of bools reporting whether each dependence is optional or mandatory.
        This information is employed while determining the import location of each dependency
        and to prepare the text of error messages.
    dependencies_extra_error_message
        Additional text, corresponding to each dependency, to be added in the error message.
        This information is only employed to prepare the text of error messages.
    pip_uninstall_call
        A function that, given the python exectuable, the pypi name of a dependency of the package,
        and the path it has actually been imported from, returns the string to be reported to
        the user on how to uninstall it with pip.

    Raises
    ------
    ImportError
        If at least a dependency is imported from user-site, or if at least a mandatory dependency
        is broken or missing.
    """
    assert len(dependencies_import_name) == len(dependencies_pypi_name), "Incorrect input lengths"
    assert len(dependencies_import_name) == len(dependencies_optional), "Incorrect input lengths"
    assert len(dependencies_import_name) == len(dependencies_extra_error_message), "Incorrect input lengths"

    allow_user_site_imports_env_name = f"{package_name}_allow_user_site_imports".upper()
    allow_user_site_imports_env_value = os.getenv(allow_user_site_imports_env_name) is not None

    if not allow_user_site_imports_env_value:
        missing_dependencies: list[str | None] = [None] * len(dependencies_import_name)
        broken_dependencies: list[dict[str, str] | None] = [
            None] * len(dependencies_import_name)
        user_site_dependencies: list[dict[str, str] | None] = [
            None] * len(dependencies_import_name)
        for (dependency_id, dependency_import_name) in enumerate(dependencies_import_name):
            dependency_module_expected_path = f"{dependencies_expected_prefix}/{dependency_import_name}/__init__.py"
            if not os.path.exists(dependency_module_expected_path) and not dependencies_optional[dependency_id]:
                missing_dependencies[dependency_id] = dependency_module_expected_path
            else:
                try:
                    dependency_module = importlib.import_module(dependency_import_name)
                except BaseException as dependency_module_import_error:
                    if not dependencies_optional[dependency_id]:
                        broken_dependencies[dependency_id] = {
                            "expected": dependency_module_expected_path,
                            "error": str(dependency_module_import_error)
                        }
                else:
                    if dependency_module.__file__ != dependency_module_expected_path:
                        assert dependency_module.__file__ is not None, f"Unable to find location of {dependency_module}"
                        user_site_dependencies[dependency_id] = {
                            "expected": dependency_module_expected_path,
                            "actual": dependency_module.__file__
                        }

        counter_error_categories = 1

        missing_dependencies_error = ""
        missing_dependencies_fix = ""
        if any([isinstance(dependency_expected_path, str) for dependency_expected_path in missing_dependencies]):
            missing_dependencies_error += f"{counter_error_categories}) Missing dependencies:\n"
            for (dependency_id, dependency_expected_path) in enumerate(missing_dependencies):
                if isinstance(dependency_expected_path, str):
                    missing_dependencies_error += (
                        f"* {dependencies_import_name[dependency_id]} is missing. "
                        f"Its expected path was {dependency_expected_path}.\n"
                    )
            missing_dependencies_fix += f"{counter_error_categories}) To install missing dependencies:\n"
            for (dependency_id, dependency_expected_path) in enumerate(missing_dependencies):
                if isinstance(dependency_expected_path, str):
                    missing_dependencies_fix += (
                        f"* check how to install {dependencies_import_name[dependency_id]} "
                        f"with {system_manager}.\n"
                    )
            counter_error_categories += 1

        broken_dependencies_error = ""
        broken_dependencies_fix = ""
        if any([isinstance(dependency_info, dict) for dependency_info in broken_dependencies]):
            broken_dependencies_error += f"{counter_error_categories}) Broken dependencies:\n"
            for (dependency_id, dependency_info) in enumerate(broken_dependencies):
                if isinstance(dependency_info, dict):
                    broken_dependencies_error += (
                        f"* {dependencies_import_name[dependency_id]} is broken. "
                        f"Error on import was '{dependency_info['error']}'.\n"
                    )
            broken_dependencies_fix += f"{counter_error_categories}) To fix broken dependencies:\n"
            for (dependency_id, dependency_info) in enumerate(broken_dependencies):
                if isinstance(dependency_info, dict):
                    broken_dependencies_fix += (
                        f"* run '{sys.executable} -m pip show {dependencies_pypi_name[dependency_id]}' in a terminal: "
                        f"if the location field is not {os.path.dirname(os.path.dirname(dependency_info['expected']))} "
                        f"consider running "
                        f"'{pip_uninstall_call(sys.executable, dependencies_pypi_name[dependency_id], 'unknown')}' "
                        "in a terminal, because the broken dependency is probably being imported from a local path "
                        f"rather than from the path provided by {system_manager}. "
                        f"{dependencies_extra_error_message[dependency_id]}\n"
                    )
            counter_error_categories += 1

        user_site_dependencies_error = ""
        user_site_dependencies_fix = ""
        if any([isinstance(dependency_info, dict) for dependency_info in user_site_dependencies]):
            user_site_dependencies_error += (
                f"{counter_error_categories}) Dependencies imported from a local path rather than from "
                f"the path provided by {system_manager}:\n"
            )
            for (dependency_id, dependency_info) in enumerate(user_site_dependencies):
                if isinstance(dependency_info, dict):
                    user_site_dependencies_error += (
                        f"* {dependencies_import_name[dependency_id]} was imported from a local path: "
                        f"expected in {dependency_info['expected']}, but imported from {dependency_info['actual']}.\n"
                    )
            user_site_dependencies_fix += f"{counter_error_categories}) To uninstall local dependencies:\n"
            for (dependency_id, dependency_info) in enumerate(user_site_dependencies):
                if isinstance(dependency_info, dict):
                    user_site_dependencies_fix += (
                        "* run "
                        f"""'{pip_uninstall_call(
                            sys.executable, dependencies_pypi_name[dependency_id], dependency_info['actual'])}' """
                        "in a terminal, and verify that you are prompted to confirm removal of files in "
                        f"{os.path.dirname(dependency_info['actual'])}. "
                        f"{dependencies_extra_error_message[dependency_id]}\n"
                    )
            counter_error_categories += 1

        if counter_error_categories > 1:
            import_error = (
                f"pusimp has detected the following problems with {package_name} dependencies:\n"
                f"{missing_dependencies_error}"
                f"{broken_dependencies_error}"
                f"{user_site_dependencies_error}"
                "\n"
                "pusimp suggests to apply all of the following fixes:\n"
                f"{missing_dependencies_fix}"
                f"{broken_dependencies_fix}"
                f"{user_site_dependencies_fix}"
                "\n"
                f"You can disable this check by exporting the {allow_user_site_imports_env_name} environment "
                f"variable. Note, however, that this may break the installation provided by {system_manager}.\n"
                f"If you believe that this message appears incorrectly, report this at {contact_url} ."
            )
            raise ImportError(import_error)
