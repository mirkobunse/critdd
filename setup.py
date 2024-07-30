from setuptools import setup

def readme():
    with open("README.md") as f:
        return f.read()

setup(
    name="critdd",
    version="0.0.4",
    description="Critical difference diagrams with Python and Tikz",
    long_description=readme(),
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Tikz",
        "License :: OSI Approved :: GPL-3 License",
        "Development Status :: 3 - Alpha",
    ],
    keywords=[
        "machine-learning",
        "benchmark",
        "hypothesis-testing",
        "post-hoc-analysis",
    ],
    url="https://github.com/mirkobunse/critdd",
    author="Mirko Bunse",
    author_email="mirko.bunse@cs.tu-dortmund.de",
    license="GPL-3",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "scipy",
        "networkx",
    ],
    python_requires=">=3.6",
    include_package_data=True,
    zip_safe=False,
    test_suite="nose.collector",
    extras_require = {
        "tests" : ["nose", "pandas"],
        "docs" : ["myst-parser", "sphinx-rtd-theme"],
    }
)
