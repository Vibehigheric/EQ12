from setuptools import find_packages, setup

setup(
    name="EQ12SystemMonitor",
    version="1.0.0",
    description=(
        "EQ12 Python module for system health monitoring with alerting when thresholds are exceeded, "
        "CPU usage tracking, a web dashboard for configuration and viewing alerts, and additional capabilities."
    ),
    author="EQ12 System",
    author_email="admin@eq12.system",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8+",
    ],
    entry_points={
        "console_scripts": [
            "eq12systemmonitor=eq12systemmonitor:main",
        ],
    },
)
