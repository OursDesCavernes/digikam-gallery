import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="digikam-gallery",
    version="0.0.1",
    author="Thomas Coquelin",
    author_email="thomascoquelin@yahoo.fr",
    description="Web gallery based on digikam database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OursDesCavernes/digikam-gallery",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Framework :: Flask",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ""
    ],
)
