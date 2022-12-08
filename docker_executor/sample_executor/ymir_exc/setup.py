from setuptools import setup, find_packages


__version__ = '2.0.1.1123'

requirements = []
with open('requirements.txt') as f:
    for line in f.read().splitlines():
        requirements.append(line)

setup(
    name='ymir-exc',
    version=__version__,
    python_requires=">=3.7",
    install_requires=requirements,
    author_email="contact.viesc@gmail.com",
    description="ymir executor SDK: SDK for develop ymir training, mining and infer docker images",
    url="https://github.com/IndustryEssentials/ymir",
    packages=find_packages(exclude=["*tests*"]),
    include_package_data=True,
)
