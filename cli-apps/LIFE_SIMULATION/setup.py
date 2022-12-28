from setuptools import setup


def readme():
    with open("README.md", "r") as fh:
        long_description = fh.read()
        return long_description


setup(
    name='LIFE_SIMULATION',
    version='1.00',
    packages=['LIFE_SIMULATION'],
    url='https://github.com/GlobalCreativeApkDev/GlobalCreativeApkDev.github.io/tree/main/cli-apps/LIFE_SIMULATION',
    license='MIT',
    author='GlobalCreativeApkDev',
    author_email='globalcreativeapkdev2022@gmail.com',
    description='This package contains implementation of the offline adventure and simulation RPG '
                '"LIFE_SIMULATION" on command line interface.',
    long_description=readme(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.9"
    ],
    entry_points={
        "console_scripts": [
            "LIFE_SIMULATION=LIFE_SIMULATION.life_simulation:main",
        ]
    }
)