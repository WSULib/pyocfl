from setuptools import setup

setup(name='pyocfl',
	version='0.1',
	description='Python 3.x client for the Oxford Common Filesystem Layout (OCFL) specification',
	url='http://github.com/wsulib/pyocfl',
	author='Graham Hukill',
	author_email='ghukill@gmail.com',
	license='MIT License',
	install_requires=[
		'PyInstaller==3.4',
		'pypairtree==1.1.0',
		'pytest==4.0.1'
	],
	packages=['pyocfl'],
	zip_safe=False
)
