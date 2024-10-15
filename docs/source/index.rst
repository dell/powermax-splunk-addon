..  toctree::
    :maxdepth: 2
    :hidden:

    overview
    installation
    configuration
    metrics
    support

Welcome to the official PowerMax for Splunk documentation!
==========================================================

Overview
--------
PowerMax for Splunk provides Splunk users with a backend Technology Add-on (TA)
and frontend app to simplify interaction with Splunk Enterprise environments.

The Splunk Technology Add-on for PowerMax allows a Splunk Enterprise
administrator to collect inventory, performance information, alert, and audit
log information from VMAX/PowerMax storage arrays. The TA is a wrapper
around the opensource library PyU4V_, providing programmatic access to the
Unisphere for PowerMax REST API.  You can directly analyse data use it as a
contextual data feed to correlate with other operational or security data in
Splunk Enterprise.

The Splunk App for Dell EMC PowerMax allows a Splunk Enterprise administrator
to data from PowerMax arrays through the TA and present them in pre-built
dashboards, tables, and time charts for in-depth analysis.

The TA and App can be downloaded from the links below:

- `Dell EMC PowerMax Add-on for Splunk Enterprise`_
- `Dell EMC PowerMax App for Splunk Enterprise`_

From the PowerMax for Splunk 3.x release code for both the TA and app will be
actively managed and maintained from the public Dell GitHub repo. The source
for both code can be viewed and downloaded from the links below:

- `Dell EMC PowerMax Add-on for Splunk Enterprise source`_
- `Dell EMC PowerMax App for Splunk Enterprise source`_


Version Info
------------
+---------------------------------+----------------------------------------+
| **PowerMax for Splunk**         | 5.0.0                                 |
+---------------------------------+----------------------------------------+
| **Technology Add-On**           | 5.0.0                                  |
+---------------------------------+----------------------------------------+
| **Minimum Unisphere Version**   | 10.0.0                                 |
+---------------------------------+----------------------------------------+
| **Array Model**                 | VMAX-3, VMAX AFA, PowerMax             |
+---------------------------------+----------------------------------------+
| **Array uCode**                 | HyperMax OS, PowerMax OS               |
+---------------------------------+----------------------------------------+
| **Minimum Splunk Version**      | Splunk Enterprise 8.2                  |
+---------------------------------+----------------------------------------+
| **Platforms**                   | Linux, Windows                         |
+---------------------------------+----------------------------------------+
| **Python**                      | Splunk Native 3.7                      |
+---------------------------------+----------------------------------------+

.. note::
    For PowerMax 2500 and 8500 models, minimum operating environment of PowerMax OS 10 and Management Software Unisphere
    for PowerMax version 10. For older PowerMax models Unisphere 10 is required.

.. note::
    PowerMax for Splunk has been tested and verified only against Python 3.x.
    There is **no** support for Python 2.x, it reached end-of-life in
    January 2020.


Getting Started
---------------
:doc:`overview`
    About the TA and App, what's new, contact information, and hours of
    operation.

:doc:`installation`
    Supported versions, enabling performance metrics collection in Unisphere,
    configuring Unisphere users permissions for Splunk, SSL configuration, and
    installing the TA and App.

:doc:`configuration`
    Configuring PowerMax for Splunk TA and App for your environment.

:doc:`metrics`
    Detailed list of all Splunk supported Unisphere performance category
    metrics.

:doc:`support`
    How to get open issues or get support for PowerMax for Splunk.


Build your own Docs
-------------------
PowerMax for Splunk docs have been included with the PowerMax for Splunk TA and
App source code, if you would like to build the docs from scratch to view
locally use the following commands:

.. code-block:: bash

   $ pip install sphinx
   $ pip install sphinx-rtd-theme
   $ cd {powermax_for_splunk}/docs
   $ make clean && make html

All of the necessary ``make`` files and Sphinx configuration files are included
with PowerMax for Splunk so you can build the docs after the required
dependencies have been installed.

Once the above commands have been run you will find newly generated html files
within the ``{powermax_for_splunk}/docs/build`` folder. Open ``index.html``
within a browser of your choosing to view the docs offline. Generating the docs
is not required, we have bundled the most up-to-date docs with PowerMax for
Splunk so you can still navigate to
``{powermax_for_splunk}/docs/build/index.html`` within your browser to view
PowerMax for Splunk docs offline.


Disclaimer
----------
PowerMax for Splunk 3.x is distributed under the Splunk EULA for Third-Party
Content. Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an **"as is" basis, without
warranties conditions of any kind**, either express or implied. See the
`License`_ for the specific language governing permissions and limitations under
the License.


.. URL LINKS

.. _PyU4V: https://github.com/dell/PyU4V
.. _`Dell EMC PowerMax Add-on for Splunk Enterprise`: https://splunkbase.splunk.com/app/3416/
.. _`Dell EMC PowerMax App for Splunk Enterprise`: https://splunkbase.splunk.com/app/3467/
.. _`Dell EMC PowerMax Add-on for Splunk Enterprise source`: https://github.com/dell/powermax-splunk-addon
.. _`Dell EMC PowerMax App for Splunk Enterprise source`: https://github.com/dell/powermax-splunk-app
.. _License: https://github.com/dell/powermax-splunk-addon/blob/master/LICENSE
