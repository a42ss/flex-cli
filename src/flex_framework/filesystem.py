from __future__ import annotations

import os
from typing import List, Optional, Type

from .api.factory import Factory
from .config.exception import FilesystemException


class FilePermission:
    _stat: Optional[os.stat_result] = None
    file: Optional[str] = None

    def get_stat(self):
        if self._stat is None:
            self._stat = os.stat(self.file)
        return self._stat

    def get_permission(self):
        return oct(self.get_stat().st_mode)

    def get_file(self) -> str:
        if self.file is None:
            raise FilesystemException("Empty file name provided for permission check.")
        return self.file

    def check_others_have(self, permission: int) -> bool:
        other_permission = int(self.get_permission()[-1:])
        return other_permission & permission == permission

    def access(self, permission: int) -> bool:
        return os.access(self.get_file(), permission)


class FilePermissionFactory(Factory):
    def create(
        self,
        class_name: Type[FilePermission] = FilePermission,
        data: Optional[dict] = None,
    ) -> FilePermission:
        return super().create(class_name, data)


class FileDiscoveryChecks(tuple):
    PERMISSION_CHECK_NONE = 0
    PERMISSION_CHECK_W = os.W_OK
    PERMISSION_CHECK_R = os.R_OK
    PERMISSION_CHECK_X = os.X_OK

    def __init__(
        self,
        user_access: int,
        others_allow: int,
        others_deny: int,
        extensions: List[str],
    ):
        pass

    @staticmethod
    def __new__(cls: Type, *args, **kwargs):
        return tuple.__new__(FileDiscoveryChecks, args)

    user_access: property = property(lambda self: self[0])
    others_allow: property = property(lambda self: self[1])
    others_deny: property = property(lambda self: self[2])
    extensions: property = property(lambda self: self[3])


class FileDiscovery:
    file_permission_factory: FilePermissionFactory

    def __init__(self, file_permission_factory: FilePermissionFactory):
        self.file_permission_factory = file_permission_factory

    def get_available_files(
        self, directories: List[str], file_checks: Optional[FileDiscoveryChecks] = None
    ) -> List[str]:
        result = []

        for directory in directories:
            if os.path.isdir(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_abs_path = os.path.join(root, file)
                        file_permission = self.file_permission_factory.create(
                            FilePermission, {"file": file_abs_path}
                        )
                        if file_checks is not None and self.check_extensions(
                            file, file_checks
                        ):
                            if not file_permission.access(file_checks.user_access):
                                raise FilesystemException(
                                    "Execute permission missing for current user on file: "
                                    + file_abs_path
                                )

                            if file_permission.check_others_have(
                                file_checks.others_deny
                            ):
                                raise FilesystemException(
                                    "Remove write permission for others on file: "
                                    + file_abs_path
                                )

                            result.append(file_abs_path)
        return result

    def check_extensions(self, file: str, file_checks: FileDiscoveryChecks):
        for extension in file_checks.extensions:
            if file.endswith("." + extension):
                return True
        return False
