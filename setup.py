from setuptools import setup
# setuptools used instead of distutils.core so that 
# dependencies can be handled automatically

setup(
    name='graphserver',
    version='0.1',
    packages=['graphserver'],
    scripts=['graphserver.py'],
    classifiers=["Development Status :: 3 - Alpha",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: Apache Software License",
                 "Operating System :: OS Independent", #is this true? know Linux & OS X ok
                 "Programming Language :: Python",
                 "Programming Language :: Python :: 2.6",
                 "Programming Language :: Python :: 2.7",
                 "Topic :: Internet :: WWW/HTTP",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Environment :: Web Environment"],
    author='Simeon Warner',
    author_email='simeon.warner@cornell.edu',
    description='Web graph server to simulate scenarios for signposting the scholarly web',
    long_description=open('graphserver.md').read(),
    url='http://github.com/zimeon/signposting',
    install_requires=[
        "negotiator>=1.0",
        "pydot>=1.0.28"
    ],
    test_suite="resync.test",
)
