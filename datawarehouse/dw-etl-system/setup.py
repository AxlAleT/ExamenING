from setuptools import setup, find_packages

setup(
    name='dw-etl-system',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A Data Warehouse ETL system for generating fact tables based on a SQL schema.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'sqlalchemy',
        'psycopg2-binary',  # or another database driver as needed
        'python-dotenv',
    ],
    entry_points={
        'console_scripts': [
            'dw-etl=main:main',  # Adjust this if your main function is located elsewhere
        ],
    },
)