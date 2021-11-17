from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in ldapsync/__init__.py
from ldapsync import __version__ as version

setup(
	name="ldapsync",
	version=version,
	description="Sync ERPNext Contacts to LDAP or Active Directory",
	author="itsdave",
	author_email="dev@itsdave.de",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
