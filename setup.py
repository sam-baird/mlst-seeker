from setuptools import find_packages, setup

setup(
    name="mlst-seeker",
    packages=find_packages(),
    package_dir={"src": "src"},
    entry_points={
        "console_scripts": [
            "mlst-seeker=src.mlstseeker.main:main"
        ]
    }
)