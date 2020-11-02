from setuptools import find_packages, setup

setup(
    name="django_video_encoder",
    description="Simple integration of a Django model with a FileField to encoding backends",  # NoQA: E501
    long_description=open("README.rst").read(),
    author="Jonas und der Wolf GmbH",
    author_email="opensource@jonasundderwolf.de",
    url="http://github.com/jonasundderwolf/django-video-encoder",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
