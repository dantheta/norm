
import os
from setuptools import setup


setup(
	name = 'NORM',
	version = '0.8.2',
	author = 'Daniel Ramsay',
	author_email = 'daniel@dretzq.org.uk',

	license = 'BSD',
	url = 'http://www.github.com/dantheta/norm',
	packages = ['NORM'],
	
	description = 'NORM - not an ORM, a simple table mapper for Python.',
	requires = ['psycopg2'],
)
