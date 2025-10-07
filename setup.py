"""
Setup script for Focus Server Automation Framework
"""

from setuptools import setup, find_packages

setup(
    name="focus-server-automation-framework",
    version="1.0.0",
    description="Professional Test Automation Framework for Focus Server",
    author="Senior QA Automation Architect",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pytest>=7.4.0",
        "requests>=2.31.0",
        "pydantic>=2.4.0",
        "pyyaml>=6.0.1",
        "kubernetes>=28.1.0",
        "pymongo>=4.6.0",
        "paramiko>=3.3.1",
    ],
)
