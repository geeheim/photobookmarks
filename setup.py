from setuptools import setup, find_packages

# Read the long description from a README file
with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="update_photo_bookmarks",
    version="0.1.0",
    author="Geert Heilmann",
    author_email="geert.heilmann@googlemail.com",
    description="A module for managing photo bookmarks in a mac OS photo librarydatabase",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geeheim/update_photo_bookmarks",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        
    ],
    entry_points={
        'console_scripts': [
            'update-photo-bookmarks=update_photo_bookmarks:main',
        ],
    },
)