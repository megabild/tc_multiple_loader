# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='tc_multiple_loader',
    version='1.0.0',
    url='https://megabild.de',
    license='MIT',
    author='crothhass',
    description='Thumbor multiple loader extension',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'thumbor>=5.0.6',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
