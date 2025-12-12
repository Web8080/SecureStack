from setuptools import setup, find_packages

setup(
    name="securestack-client",
    version="1.0.0",
    description="Python client for SecureStack DevSecOps Platform",
    author="SecureStack",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
        "httpx>=0.25.0"
    ],
    python_requires=">=3.8",
)


