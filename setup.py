from setuptools import setup, find_namespace_packages


setup(
    name="weatherapp.sinoptik",
    version="0.1.0",
    author="Vasyl Rostykus",
    description="SinoptikWeather provider",
    long_description="",
    packages=find_namespace_packages(),
    entry_points={
        'weatherapp.provider': 'sinoptik=weatherapp.sinoptik.provider:SinoptikProvider',
    },
    install_requires=[
        'requests',
        'bs4',
    ],
)
