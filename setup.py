#!/usr/bin/env python

"""The setup script."""

import pip
from setuptools import setup, find_packages

try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


## workaround derived from: https://github.com/pypa/pip/issues/7645#issuecomment-578210649
parsed_requirements = parse_requirements(
    'requirements/prod.txt',
    session='workaround'
)

parsed_test_requirements = parse_requirements(
    'requirements/test.txt',
    session='workaround'
)

try:
    requirements = [str(ir.req) for ir in parsed_requirements]
    test_requirements = [str(tr.req) for tr in parsed_test_requirements]
except AttributeError:
    requirements = [str(ir.requirement) for ir in parsed_requirements]
    test_requirements = [str(tr.requirement) for tr in parsed_test_requirements]

setup(
    author="Laurent Radoux",
    author_email='radoux.laurent@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Notifies a WaniKani user for new reviews to do.",
    entry_points={
        'console_scripts': [
            'wanikani_notifier=wanikani_notifier.cli:cli',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='wanikani_notifier',
    name='wanikani_notifier',
    packages=find_packages(include=['wanikani_notifier', 'wanikani_notifier.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/laurent-radoux/wanikani_notifier',
    version='0.5.2',
    zip_safe=False,
)
