# Copyright (C) 2023-2026 by the pusimp authors
#
# This file is part of pusimp.
#
# SPDX-License-Identifier: MIT
"""Utility functions used while testing the package.

Note that this file does not get automatically imported in __init__.py to avoid having a runtime dependency
on virtualenv.
"""

import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import types
import typing

import virtualenv


def assert_has_package(executable: str, package: str) -> None:
    """Assert that a package is installed.

    Note that it is not safe to simply import the package in the current pytest environment,
    since the environment itself might change from one test to the other, but python packages
    can be imported only once and not unloaded.
    """
    run_import = subprocess.run(f"{executable} -c 'import {package}'", shell=True, capture_output=True)
    assert run_import.returncode == 0, (
        f"Importing {package} was not successful.\n"
        f"stdout contains {run_import.stdout.decode().strip()}\n"
        f"stderr contains {run_import.stderr.decode().strip()}"
    )


def assert_not_has_package(executable: str, package: str) -> None:
    """Assert that a package is not installed."""
    run_import = subprocess.run(f"{executable} -c 'import {package}'", shell=True, capture_output=True)
    assert run_import.returncode != 0, f"Importing {package} was unexpectedly successful"


def assert_package_location(executable: str, package: str, package_path: str) -> None:
    """Assert that a package imports from the expected location."""
    assert_has_package(executable, package)
    run_import_file = subprocess.run(
        f"{executable} -c 'import {package}; print({package}.__file__)'", shell=True, capture_output=True)
    assert run_import_file.returncode == 0, (
        "This case was never supposed to happen, because {package} did import successfully with assert_has_package")
    assert run_import_file.stdout.decode().strip() == package_path, (
        f"{package} was expected at {package_path}, but found at {run_import_file.stdout.decode().strip()}")


def assert_package_import_error(
    executable: str, package: str, expected: typing.List[str], not_expected: typing.List[str], verbose: bool
) -> None:
    """Assert that a package fails to imports with the expected text in the ImportError message."""
    run_import = subprocess.run(f"{executable} -c 'import {package}'", shell=True, capture_output=True)
    assert run_import.returncode != 0, f"Importing {package} was unexpectedly successful"
    import_error_text = (
        f"Importing {package} was not successful.\n"
        f"stdout contains {run_import.stdout.decode().strip()}\n"
        f"stderr contains {run_import.stderr.decode().strip()}")
    if verbose:
        print(f"Package {package} did fail to import with error:\n{import_error_text}")
    for expected_ in expected:
        assert expected_ in import_error_text, (
            f"'{expected_}' was not found in the ImportError text, namely '{import_error_text}'"
        )
    for not_expected_ in not_expected:
        assert not_expected_ not in import_error_text, (
            f"'{not_expected_}' was unexpectedly found in the ImportError text, namely '{import_error_text}'"
        )


class TemporarilyEnableEnvironmentVariable:
    """Temporarily enable an environment variable in a test."""

    def __init__(self, variable_name: str) -> None:
        self._variable_name = variable_name

    def __enter__(self) -> None:
        """Temporarily set the environment variable."""
        assert self._variable_name not in os.environ, f"{self._variable_name} was already found in the environment"
        os.environ[self._variable_name] = "enabled"

    def __exit__(
        self, exception_type: typing.Optional[typing.Type[BaseException]],
        exception_value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType]
    ) -> None:
        """Unset the enviornment variable."""
        del os.environ[self._variable_name]


class VirtualEnv:
    """Helper class to create a temporary virtual environment.

    Forked and simplified from https://github.com/pyscaffold/pyscaffold/blob/master/tests/virtualenv.py .
    """

    def __init__(self) -> None:
        self.path = pathlib.Path(tempfile.mkdtemp()) / "venv"
        self.dist_path = (
            self.path / "lib" / ("python" + str(sys.version_info.major) + "." + str(sys.version_info.minor))
            / "site-packages"
        )
        self.executable = str(self.path / "bin" / "python3")
        self.env = dict(os.environ)
        self.env.pop("PYTHONPATH", None)  # ensure isolation

    def __enter__(self) -> "VirtualEnv":
        """Create the virtual environment."""
        assert not self.path.exists(), f"{self.path} already exists"
        self.create()
        return self

    def __exit__(
        self, exception_type: typing.Optional[typing.Type[BaseException]],
        exception_value: typing.Optional[BaseException],
        traceback: typing.Optional[types.TracebackType]
    ) -> None:
        """Delete the virtual environment."""
        shutil.rmtree(str(self.path.parent), ignore_errors=True)

    def create(self) -> None:
        """Create a virtual environment, and add it to sys.path."""
        args = [str(self.path), "--python", sys.executable, "--system-site-packages", "--no-wheel"]
        virtualenv.cli_run(args, env=self.env)
        # virtualenv does not necessarily ship the same version of pip as the underlying environment
        run_update_pip = subprocess.run(
            f"{self.executable} -m pip install --upgrade --break-system-packages pip",
            shell=True, env=self.env, capture_output=True)
        if run_update_pip.returncode != 0:  # pragma: no cover
            # it is possible that the version of pip shipped by virtualenv was not recent enough
            # to support --break-system-packages. The newly installed version will surely support
            # --break-system-packages, so we can always add that flag in self.install_package
            run_update_pip_again = subprocess.run(
                f"{self.executable} -m pip install --upgrade pip", shell=True, capture_output=True)
            assert run_update_pip_again.returncode == 0, "Failed to upgrade pip"

    def install_package(
        self, package: str, install_call: typing.Optional[typing.Callable[[str, str], str]] = None
    ) -> None:
        """Install a package in the virtual environment."""
        if install_call is None:
            install_call = self._default_install_call
        run_install = subprocess.run(
            install_call(self.executable, package), shell=True, env=self.env, capture_output=True)
        if run_install.returncode != 0:
            raise RuntimeError(
                f"Installing {package} was not successful.\n"
                f"stdout contains {run_install.stdout.decode()}\n"
                f"stderr contains {run_install.stderr.decode()}"
            )

    @staticmethod
    def _default_install_call(executable: str, package: str) -> str:
        """Return the default call to pip install."""
        return f"{executable} -m pip install --ignore-installed --break-system-packages {package}"

    def break_package(self, package: str) -> None:
        """Install a mock package in the virtual environment which errors out."""
        (self.dist_path / package).mkdir()
        with (self.dist_path / package / "__init__.py").open("w") as init_file:
            init_file.write(f"raise ImportError('{package} was purposely broken.')")

    def uninstall_package(
        self, package: str, installation_path: str,
        uninstall_call: typing.Optional[typing.Callable[[str, str, str], str]] = None
    ) -> None:
        """Uninstall a package from the virtual environment."""
        if uninstall_call is None:
            uninstall_call = self._default_uninstall_call
        run_uninstall = subprocess.run(
            uninstall_call(self.executable, package, installation_path), shell=True, env=self.env, capture_output=True)
        if (
            run_uninstall.returncode != 0
                or
            (
                run_uninstall.returncode == 0
                    and
                f"WARNING: Skipping {package} as it is not installed" in run_uninstall.stderr.decode()
            )
        ):
            raise RuntimeError(
                f"Uninstalling {package} was not successful.\n"
                f"stdout contains {run_uninstall.stdout.decode()}\n"
                f"stderr contains {run_uninstall.stderr.decode()}"
            )

    @staticmethod
    def _default_uninstall_call(executable: str, package: str, installation_path: str) -> str:
        """Return the default call to pip uninstall."""
        return f"{executable} -m pip uninstall --yes --break-system-packages {package}"


def assert_package_import_success_without_local_packages(package: str, package_path: str) -> None:
    """Assert that the package imports correctly without any local packages."""
    assert_package_location(sys.executable, package, package_path)


def assert_package_import_errors_with_local_packages(
    package: str, dependencies_import_name: typing.List[str], dependencies_pypi_name: typing.List[str],
    dependencies_extra_error_message: typing.List[str], pip_install_call: typing.Callable[[str, str], str],
    pip_uninstall_call: typing.Callable[[str, str, str], str]
) -> None:
    """Assert that a package fails to import with local packages, but imports successfully when they are uninstalled."""
    with VirtualEnv() as virtual_env:
        # Part 1: assert that the package fails to import with local packages
        dependencies_local_paths = []
        for (dependency_import_name, dependency_pypi_name) in zip(dependencies_import_name, dependencies_pypi_name):
            virtual_env.install_package(dependency_pypi_name, pip_install_call)
            dependency_local_path = str(virtual_env.dist_path / dependency_import_name / "__init__.py")
            assert_package_location(virtual_env.executable, dependency_import_name, dependency_local_path)
            dependencies_local_paths.append(dependency_local_path)
        dependencies_error_messages = [
            f"* {dependency_import_name} was imported from a local path: expected in"
            for dependency_import_name in dependencies_import_name
        ]
        dependencies_pypi_name_only = [
            dependency_pypi_name.replace("'", "").split("@")[0].strip()  # from 'name @ git+url' to name
            for dependency_pypi_name in dependencies_pypi_name
        ]
        dependencies_error_messages.extend(
            f"* run '{pip_uninstall_call(virtual_env.executable, dependency_pypi_name, dependency_local_path)}' in"
            for (dependency_pypi_name, dependency_local_path) in zip(
                dependencies_pypi_name_only, dependencies_local_paths)
        )
        dependencies_error_messages.extend(dependencies_extra_error_message)
        assert_package_import_error(virtual_env.executable, package, dependencies_error_messages, [], True)
        # Part 2: assert that the package imports successfully as soon as local packages are uninstalled
        for (dependency_pypi_name, dependency_local_path) in zip(dependencies_pypi_name_only, dependencies_local_paths):
            virtual_env.uninstall_package(
                dependency_pypi_name, dependency_local_path, _force_yes_in_pip_uninstall_call(pip_uninstall_call))
        assert_has_package(virtual_env.executable, package)


def _force_yes_in_pip_uninstall_call(
    pip_uninstall_call: typing.Callable[[str, str, str], str]
) -> typing.Callable[[str, str, str], str]:
    """Force pip uninstall --yes even when a plain pip uninstall is provided."""
    def _(executable: str, package: str, installation_path: str) -> str:
        base_call = pip_uninstall_call(executable, package, installation_path)
        if " -y " not in base_call and " --yes " not in base_call:
            base_call = base_call.replace(" uninstall ", " uninstall -y ")
        return base_call

    return _


def assert_package_import_success_with_allowed_local_packages(
    package: str, package_path: str, dependencies_import_name: typing.List[str],
    dependencies_pypi_name: typing.List[str], pip_install_call: typing.Callable[[str, str], str]
) -> None:
    """Assert that a package imports correctly even with extra local packages when asked to allow user-site imports."""
    with VirtualEnv() as virtual_env:
        for (dependency_import_name, dependency_pypi_name) in zip(dependencies_import_name, dependencies_pypi_name):
            virtual_env.install_package(dependency_pypi_name, pip_install_call)
            assert_package_location(
                virtual_env.executable, dependency_import_name,
                str(virtual_env.dist_path / dependency_import_name / "__init__.py")
            )
        with TemporarilyEnableEnvironmentVariable(f"{package}_allow_user_site_imports".upper()):
            assert_package_location(virtual_env.executable, package, package_path)


def assert_package_import_errors_with_broken_non_optional_packages(
    package: str, dependencies_import_name: typing.List[str], dependencies_optional: typing.List[bool]
) -> None:
    """Assert that a package fails to import when non-optional packages are broken."""
    with VirtualEnv() as virtual_env:
        for (dependency_import_name, dependency_optional) in zip(dependencies_import_name, dependencies_optional):
            if not dependency_optional:
                virtual_env.break_package(dependency_import_name)
                assert_package_import_error(
                    virtual_env.executable, dependency_import_name,
                    [f"{dependency_import_name} was purposely broken."], [], False
                )
        dependencies_expected_error_messages = [
            f"* {dependency_import_name} is broken"
            for (dependency_import_name, dependency_optional) in zip(dependencies_import_name, dependencies_optional)
            if not dependency_optional
        ]
        dependencies_not_expected_error_messages = [
            f"* {dependency_import_name} is broken"
            for (dependency_import_name, dependency_optional) in zip(dependencies_import_name, dependencies_optional)
            if dependency_optional
        ]
        assert_package_import_error(
            virtual_env.executable, package, dependencies_expected_error_messages,
            dependencies_not_expected_error_messages, True
        )


def assert_package_import_success_with_broken_optional_packages(
    package: str, package_path: str, dependencies_import_name: typing.List[str],
    dependencies_optional: typing.List[bool]
) -> None:
    """Assert that a package imports correctly when optional packages are broken."""
    with VirtualEnv() as virtual_env:
        for (dependency_import_name, dependency_optional) in zip(dependencies_import_name, dependencies_optional):
            if dependency_optional:
                virtual_env.break_package(dependency_import_name)
                assert_package_import_error(
                    virtual_env.executable, dependency_import_name,
                    [f"{dependency_import_name} was purposely broken."], [], False
                )
        assert_package_location(virtual_env.executable, package, package_path)
