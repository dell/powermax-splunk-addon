"""setup.py."""

import setuptools

"""
NOTE: The PowerMax for Splunk add-on should not be installed in Splunk
environments using PIP. This pip install functionality is required only for 
running TOX unit tests or CI tests. To install the PowerMax for Splunk add-on
for production environments please install via the Splunk UI or download 
from SplunkBase.
"""

setuptools.setup(
    name='PowerMaxSplunkAddOnTestSuite',
    version='3.0.0.0',
    url='https://github.com/dell/splunk/',
    author='Dell Inc. or its subsidiaries',
    author_email='Michael.Mcaleer@dell.com',
    description="PowerMax for Splunk standalone install for testing.",
    packages=setuptools.find_packages(),
    install_requires=['requests', 'six', 'urllib3'],
    include_package_data=True,
    python_requires='>=3.6, <=3.9',
    tests_require=['pytest', 'pytest-cov', 'mock', 'testtools'],
    test_suite='tests')
