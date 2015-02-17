import finddata
from setuptools import setup, find_packages

setup(
    name="django_zencoder",
    author="Jonas und der Wolf",
    author_email="info@jonasunderwolf.de",
    version="0.5",
    packages=find_packages(),
    package_data=finddata.find_package_data(),
    include_package_data=True,
)
