from setuptools import setup, find_packages

setup(
    name='excise_tools',
    version='0.0.1',
    description='Excise duty and customs tools for ERPNext',
    author='Premitium',
    author_email='info@example.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['frappe']
)
