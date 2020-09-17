from setuptools import setup, find_packages

with open('README.md', "r") as readme_file:
    readme = str(readme_file.read())

with open('requirements.txt', 'r') as requirements_file:
    install_requires = [line for line in requirements_file]

setup(
    name="pytorch-deployment-tutorial",
    version="1.0.0.dev0",
    description="My first deployment with pesto",
    long_description=readme + '\n\n',
    author="Computer Vision",
    author_email='computervision@airbus.com',
    url="",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    keywords=["pesto-project"],
)
