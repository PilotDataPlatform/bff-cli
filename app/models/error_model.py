# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class ValidationError(Exception):
    def __init__(self, message='Validation Failed'):
        super().__init__(message)
        self.error_msg = message


class InvalidEncryptionError(Exception):
    def __init__(self, message='Invalid encryption'):
        super().__init__(message)


class HPCError(Exception):
    def __init__(self, code, message='HPC error'):
        self.code = code
        self.error_msg = message
        super().__init__(message)

    def __str__(self) -> str:
        return f'{self.code}: {self.error_msg}'
