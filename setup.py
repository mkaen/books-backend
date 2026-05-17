from pathlib import Path

from setuptools import setup, find_packages

_ROOT = Path(__file__).parent / "src" / "__init__.py"
_metadata = {}
exec(_ROOT.read_text(), _metadata)

setup(
    name=_metadata["NAME"],
    version=_metadata["VERSION"],
    author=_metadata["AUTHOR"],
    url=_metadata["URL"],
    package_dir={"": "."},
    packages=find_packages(where=".", include=["src*"]),
    classifiers=[
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.12",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    install_requires=[
        "Flask~=3.0.3",
        "Flask-Cors==4.0.0",
        "Flask-SQLAlchemy~=3.1.1",
        "Flask-Login~=0.6.3",
        "SQLAlchemy~=2.0.35",
        "Werkzeug~=3.0.4",
        "python-dotenv~=1.0.1",
        "requests~=2.32.4",
        "psycopg2-binary~=2.9.9",
        "alembic~=1.17.2",
        "marshmallow~=3.23.0",
    ],
    extras_require={
        "test": [
            "pytest~=8.3.3",
        ],
        "prod": [
            "gunicorn~=23.0.0",
        ],
    },
    test_suite="tests",
)
