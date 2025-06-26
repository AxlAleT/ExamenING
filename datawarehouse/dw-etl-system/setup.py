from setuptools import setup, find_packages

setup(
    name='dw-etl-system',
    version='0.1.0',
    author='axltorres',
    author_email='axltorres@example.com',
    description='An ETL system for food delivery order data warehouse using Apache Airflow',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'numpy',
        'sqlalchemy',
        'mysqlclient',
        'pymysql',
        'apache-airflow==2.7.1',
        'apache-airflow-providers-mysql',
        'pytest',
        'python-dotenv',
        'pyyaml',
        'tqdm'
    ],
    entry_points={
        'console_scripts': [
            'order-etl=main:main',
        ],
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)