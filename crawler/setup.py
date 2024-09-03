from setuptools import find_packages
from setuptools import setup

with open("requirements.txt") as f:
    content = f.readlines()
requirements = [x.strip() for x in content]

setup(
    name="crawler",
    version="0.1",
    description="Python-based tool to retrieve EPDs from different websites.",
    packages=find_packages(),
    install_requires=requirements,
    test_suite="tests",
    # include_package_data: to install data from MANIFEST.in
    include_package_data=True,
    #scripts=["scripts/crawler-run"],
    zip_safe=False,
)
