from setuptools import setup, find_namespace_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

packages = list(filter(lambda x: x.startswith("ancs4linux"), find_namespace_packages()))

setup(
    name="ancs4linux",
    version="1.0.0",
    description="Control your iOS device from Linux desktop",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Paweł Zmarzły",
    author_email="pawo2500@gmail.com",
    url="https://github.com/pzmarzly/ancs4linux",
    project_urls={
        "Source": "https://github.com/pzmarzly/ancs4linux/",
    },
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    # classifiers=[  # Optional
    #     "Development Status :: 3 - Alpha",
    #     "Intended Audience :: Developers",
    #     "Topic :: Software Development :: Build Tools",
    #     "License :: OSI Approved :: MIT License",
    #     "Programming Language :: Python :: 3",
    #     "Programming Language :: Python :: 3 :: Only",
    # ],
    # keywords="sample, setuptools, development",
    package_dir={"": "."},
    packages=packages,
    python_requires=">=3.7",
    install_requires=["click", "dasbus"],
    extras_require={
        "test": ["mypy", "black"],
    },
    data_files=[("lib/systemd/system", ["systemd/ancs4linux-server.service"])],
    entry_points={
        "console_scripts": [
            "ancs4linux-server=ancs4linux.server.main:main",
            "ancs4linux-ctl=ancs4linux.ctl.main:main",
        ],
    },
)
