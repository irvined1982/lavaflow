import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README')).read()

setup(
		zip_safe=False,
		name='django-lavaflow',
		version='1.1',
		packages=['lavaFlow'],
		include_package_data=True,	
		license="GPL 3",
		description="LavaFlow creates useful reports on the usage of high performance compute clusters. LavaFlow takes data from the batch scheduling system, monitoring, and other tooling, and creates reports that help administrators, managers, and end users better understand their cluster environment.",
		long_description=README,
		url="http://ay60dxg.com/projects/lavaflow/",
		author="David Irvine",
		author_email="irvined@gmail.com",
		scripts=['import/lava-import-gridengine.py','import/lava-import-openlava'],
		classifiers=[
			'Environment :: Web Environment',
			'Framework :: Django',
			'Programming Language :: Python',
			'Operating System :: OS Independent',
			'Programming Language :: Python :: 2',
			'Programming Language :: Python :: 2.7',
			'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
			'Intended Audience :: Science/Research',
			'Intended Audience :: System Administrators',
			'Topic :: Scientific/Engineering',
			'Topic :: Scientific/Engineering :: Information Analysis',
			],
		)
