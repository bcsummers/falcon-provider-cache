# -*- coding: utf-8 -*-
"""Setup for falcon-provider-redis package."""
# standard library
import os

# third-party
from setuptools import find_packages, setup

metadata = {}
metadata_file = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'falcon_provider_cache', '__metadata__.py'
)
with open(metadata_file, mode='r', encoding='utf-8',) as f:
    # load metadat into a dict
    exec(f.read(), metadata)  # nosec; pylint: disable=exec-used

if not metadata:
    raise RuntimeError(f'Could not load metadata file ({metadata_file}).')

# read README file to be used as long description
with open('README.rst', 'r') as f:
    readme = f.read()

dev_packages = [
    'bandit',
    'black',
    'flake8',
    # isort 5 currently causes issues with pylint
    'isort>=4,<5',
    'pre-commit',
    'pycodestyle',
    'pydocstyle',
    'pylint',
    'pytest',
    'pytest-cov',
    'pytest-html',
    'pytest-xdist',
    'pyupgrade',
    'radon',
    'xenon',
    'falcon-provider-memcache @ git+https://github.com/bcsummers/falcon-provider-memcache@master',
    'falcon-provider-redis @ git+https://github.com/bcsummers/falcon-provider-redis@master',
]
extras_require = {
    'redis': [
        'falcon-provider-redis @ git+https://github.com/bcsummers/falcon-provider-redis@master',
    ],
    'memcache': [
        (
            'falcon-provider-memcache @ '
            'git+https://github.com/bcsummers/falcon-provider-memcache@master',
        )
    ],
    'dev': dev_packages,
    'develop': dev_packages,
    'development': dev_packages,
}

setup(
    author=metadata['__author__'],
    author_email=metadata['__author_email__'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Falcon',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    description=metadata['__description__'],
    download_url=metadata['__download_url__'],
    extras_require=extras_require,
    include_package_data=True,
    install_requires=['falcon'],
    license=metadata['__license__'],
    long_description=readme,
    long_description_content_type='text/x-rst',
    name=metadata['__package_name__'],
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_dir={'falcon_provider_cache': 'falcon_provider_cache'},
    project_urls={
        'Documentation': 'https://github.com/bcsummers/falcon-provider-cache/',
        'Source': 'https://github.com/bcsummers/falcon-provider-cache/',
    },
    python_requires='>=3.6',
    scripts=[],
    test_suite='tests',
    tests_require=['pytest', 'pytest-cov'],
    url=metadata['__url__'],
    version=metadata['__version__'],
    zip_safe=True,
)
