from setuptools import setup
import src as project

setup(
    name=project.NAME,
    version=project.VERSION,
    author=project.AUTHOR,
    url=project.URL,
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.12',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    install_requires=[
        'Flask~=3.0.3',
        'Flask-Cors==4.0.0',
        'Flask-SQLAlchemy~=3.1.1',
        'Flask-Login~=0.6.3',
        'WTForms~=3.1.2',
        'SQLAlchemy~=2.0.35',
        'Werkzeug~=3.0.4',
        'DateTime~=5.5',
        'python-dotenv~=1.0.1',
        'requests~=2.32.4',
    ],
    extras_require={
        'test': [
            'pytest~=8.3.3',
        ]
    },
    test_suite='tests'
)
