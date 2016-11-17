try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

config = {
	'description': 'pifify',
	'author': 'Branden Kappes',
	'url': 'URL at which to get it.',
	'download_url': 'Where to download it.',
	'author_email': 'bkappes@mines.edu',
	'version': '0.1',
	'install_requires': ['nose'],
	'packages': ['pifify'],
	'scripts': ['bin/pifify'],
	'name': 'pifify',
}
setup(**config)
