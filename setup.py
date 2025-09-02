from setuptools import setup, find_packages

setup(
    name="payroll-accounting",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=4.2",
    ],
    entry_points={},
)
