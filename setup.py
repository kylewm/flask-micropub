"""
Flask-Micropub
--------------

This extension adds the ability to login to a Flask-based website
using IndieAuth (https://indiewebcamp.com/IndieAuth), and to request
a Micropub (https://indiewebcamp.com/Micropub) access token.
"""
from setuptools import setup


setup(
    name='Flask-Micropub',
    version='0.2.0',
    url='https://github.com/kylewm/flask-micropub/',
    license='BSD',
    author='Kyle Mahan',
    author_email='kyle@kylewm.com',
    description='Adds support for Micropub clients.',
    long_description=__doc__,
    py_modules=['flask_micropub'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'requests',
        'BeautifulSoup4',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
