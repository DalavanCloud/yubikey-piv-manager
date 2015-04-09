# Copyright (c) 2014 Yubico AB
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Additional permission under GNU GPL version 3 section 7
#
# If you modify this program, or any covered work, by linking or
# combining it with the OpenSSL project's OpenSSL library (or a
# modified version of that library), containing parts covered by the
# terms of the OpenSSL or SSLeay licenses, We grant you additional
# permission to convey the resulting work. Corresponding Source for a
# non-source form of such a combination shall include the source code
# for the parts of OpenSSL used as well as that of the covered work.


import subprocess


CMD = "yubico-piv-tool"


def check(status, err):
    if status != 0:
        raise ValueError('Error: %s' % err)


class YkPiv(object):
    def __init__(self, cmd=CMD, verbosity=0, reader=None, key=None):
        self._base_args = [cmd]
        if verbosity > 0:
            self._base_args.extend(['-v', verbosity])
        if reader:
            self._base_args.extend(['-r', reader])
        if key:
            self._base_args.extend(['-k', key])

    def run(self, *args, **kwargs):
        p = subprocess.Popen(self._base_args + list(args),
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        out, err = p.communicate(**kwargs)
        check(p.returncode, err)

        return out

    def change_pin(self, old_pin, new_pin):
        self.run('-a', 'change-pin', '-P', old_pin, '-N', new_pin)

    def change_puk(self, old_puk, new_puk):
        self.run('-a', 'change-puk', '-P', old_puk, '-N', new_puk)

    def generate(self, slot='9a'):
        return self.run('-s', slot, '-a', 'generate')

    def request_certificate(self, subject, pem, pin='123456', slot='9a'):
        return self.run('-a', 'verify-pin', '-P', pin, '-s', slot, '-a',
                        'request-certificate', '-S', subject, input=pem)
