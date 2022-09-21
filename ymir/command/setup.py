from setuptools import setup, find_packages

from mir import version

print(version.YMIR_VERSION)

# Module dependencies
requirements = []
with open('requirements.txt') as f:
    for line in f.read().splitlines():
        requirements.append(line)

setup(
    name='ymir-cmd',
    version=version.YMIR_VERSION,
    python_requires=">=3.8.10",
    author_email="contact.viesc@gmail.com",
    description="mir: A data version control tool for YMIR",
    url="https://github.com/IndustryEssentials/ymir",
    packages=find_packages(exclude=["*tests*"]),
    install_requires=requirements,
    include_package_data=True,
    entry_points={"console_scripts": ["mir = mir.main:main"]},
)
