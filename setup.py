#!/usr/bin/python3
from setuptools import setup, find_packages

setup(name='zoocli',
      version='0.2.2',
      description='Interactive ZooKeeper CLI tool.',
      author='Milosz Smolka',
      author_email='m110@m110.pl',
      url='https://github.com/m110/zoocli',
      packages=find_packages(exclude=['tests']),
      scripts=['scripts/zoocli'],
      data_files=[('/etc/zoocli', ['zoocli.conf.example'])],
      install_requires=['climb', 'kazoo'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3.4',
          'Topic :: System :: Systems Administration',
      ])
