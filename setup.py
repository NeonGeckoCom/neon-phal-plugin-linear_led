# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from setuptools import setup, find_packages
from os import path, getenv

PLUGIN_ENTRY_POINT = "neon-phal-plugin-linear-led-smbus=neon_phal_plugin_linear_led.smbus_led:SmbusLinearLed"
ADMIN_PLUGIN_ENTRY_POINT = "neon-phal-plugin-linear-led-neopixel=neon_phal_plugin_linear_led.neopixel_led:NeopixelLinearLed"
BASE_PATH = path.abspath(path.dirname(__file__))


def get_requirements(requirements_filename: str):
    requirements_file = path.join(BASE_PATH, requirements_filename)
    with open(requirements_file, 'r', encoding='utf-8') as r:
        requirements = r.readlines()
    requirements = [r.strip() for r in requirements if r.strip()
                    and not r.strip().startswith("#")]

    for i in range(0, len(requirements)):
        r = requirements[i]
        if "@" in r:
            parts = [p.lower() if p.strip().startswith("git+http") else p
                     for p in r.split('@')]
            r = "@".join(parts)
        if getenv("GITHUB_TOKEN"):
            if "github.com" in r:
                requirements[i] = \
                    r.replace("github.com",
                              f"{getenv('GITHUB_TOKEN')}@github.com")
    return requirements


with open(path.join(BASE_PATH, "README.md"), "r") as f:
    long_description = f.read()

with open(path.join(BASE_PATH, "version.py"), "r", encoding="utf-8") as v:
    for line in v.readlines():
        if line.startswith("__version__"):
            if '"' in line:
                version = line.split('"')[1]
            else:
                version = line.split("'")[1]


setup(
    name='neon-phal-plugin-linear_led',
    version=version,
    license='BSD-3',
    author='Neongecko',
    author_email='developers@neon.ai',
    url='https://github.com/NeonGeckoCom/neon-phal-plugin-linear_led',
    description='Linear/Ring LED Interface',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=get_requirements('requirements/requirements.txt'),
    packages=find_packages(),
    include_package_data=True,
    entry_points={'ovos.plugin.phal': PLUGIN_ENTRY_POINT,
                  'ovos.plugin.phal.admin': ADMIN_PLUGIN_ENTRY_POINT}
)
