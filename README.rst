Welcome to PowerMax for Splunk
==============================

| |Maintenance| |OpenSource| |AskUs| |Test| |Build| |Docs|
| |Language| |PyVersions| |Unisphere| |Platform| |License|

Overview
--------
PowerMax for Splunk provides Splunk users with a backend Technology Add-on (TA)
and frontend app to simplify interaction with Splunk Enterprise environments.

Full documentation can be found in PowerMax for Splunk's `ReadTheDocs`_.

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

Version Info
------------
+---------------------------------+----------------------------------------+
| **PowerMax for Splunk**         | 6.0                                    |
+---------------------------------+----------------------------------------+
| **Technology Add-On**           | 6.0.0                                 |
+---------------------------------+----------------------------------------+
| **Minimum Unisphere Version**   | 10.2.0.0                               |
+---------------------------------+----------------------------------------+
| **Array Model**                 | VMAX-3, VMAX AFA, PowerMax, V4         |
+---------------------------------+----------------------------------------+
| **Array uCode**                 | HyperMax OS, PowerMax OS               |
+---------------------------------+----------------------------------------+
| **Minimum Splunk Version**      | Splunk Enterprise 8.2                  |
+---------------------------------+----------------------------------------+
| **Platforms**                   | Linux, Windows                         |
+---------------------------------+----------------------------------------+
| **Python**                      | Splunk Native 3.7                      |
+---------------------------------+----------------------------------------+

Note
    For PowerMax 2500 and 8500 models, minimum operating environment of PowerMax OS 10 and Management Software
    Unisphere for PowerMax version 10, for older PowerMax models Unipshere 10 is required.

Note
    PowerMax for Splunk has been tested and verified only against Python 3.x.
    There is **no** support for Python 2.x, it reached end-of-life in
    January 2020.

Installing the TA and App
-------------------------
The PowerMax for Splunk TA can be installed from the Unisphere UI in two ways:

1. Installed from local copies of the TA and App ``.spl`` files downloaded from
Splunk Base.

or...

2. Installed directly from the Splunk Enterprise UI via ``Find More Apps`` and
searching for ``PowerMax``. The TA and App will appear in the search,
simply click install for the add-on to install it in your Splunk environment.
You will need to restart to complete the installation process.

For the remainder of this section the process of installing from a local file
will be detailed.

1. Download the TA and App(Sample Dashboards) from Splunk Base.

- `Dell EMC PowerMax Add-on for Splunk Enterprise`_
- `Dell EMC PowerMax App for Splunk Enterprise`_

2. From your Splunk home screen, click the cog icon beside ``Apps`` to navigate
to the Apps section.

3. Within the Apps section, click the button ``Install App from file`` in the
top right corner of the page.

4. Click ``Choose File``, select the PowerMax Add-on for Splunk, and click
``Upload``.

5. Once the upload is complete you will be prompted to restart Splunk to
complete the installation, click ``Restart now``. When Splunk restarts,
navigate back to the home screen and you will now see a dashboard panel for the
PowerMax for Splunk TA.

6. Repeat steps 2 to 4 to install the PowerMax for Splunk App, you will not be
prompted to restart on this occasion as the App does not require it.

Configuring the TA
------------------
From the home dashboard of your Splunk Enterprise UI select the PowerMax for
Splunk Add-On from the app list on the left-side App navigation menu.

The ``Inputs`` view that opens is the list of all VMAX or PowerMax arrays
registered with this instance of Splunk Enterprise.  To add an array to the
Splunk environment click the green button in the top-right corner of the UI
``Create New Input``.

To add an array to Splunk, you must enter a number of details into Splunk
including:

- Unisphere instance & user details
- Array details
- SSL details
- Reporting metrics configuration

Note
    There is further configuration information available in the official
    PowerMax for Splunk `ReadTheDocs`_ documentation.

Configuring the App
-------------------
After configuring the PowerMax for Splunk TA with your data inputs, if you have
selected a target index for the inputs other than the default index used by
Splunk you will need to reconfigure the PowerMax for Splunk App search macros.

Note
    Search macros are reusable blocks of Search Processing Language (SPL) that
    you can insert into other searches. They are used when you want to use the
    same search logic on different parts or values in the data set dynamically.

For each of the performance and reporting categories supported by PowerMax for
Splunk TA and App there is an associated search macro that points to a
particular index to retrieve PowerMax data.

Navigate to the installation directory of the PowerMax for Splunk App which
contains all default configuration files. Copy the ``macros.conf`` file from
the App ``default`` config directory to the App ``local`` config directory:

.. code-block:: bash

    $ cd {splunk_dir}/etc/apps/Dell-EMC-app-VMAX
    $ cp default/macros.conf local/macros.conf

Edit the newly copied version of ``macros.conf`` in the ``local`` directory
so that each ``index=`` key/value pair represents the indexes in use in your
environment. Each reporting level ingested by the PowerMax for Splunk TA
corresponds to a macro in ``macros.conf`` so all will need updated.

Example:

.. code-block:: bash

    [powermax_array]
    definition = index=main sourcetype=dellemc:vmax:rest reporting_level="Array"
    iseval=0

    [powermax_srp]
    definition = index=main sourcetype=dellemc:vmax:rest reporting_level="SRP"
    iseval=0

Becomes..

.. code-block:: bash

    [powermax_array]
    definition = index=powermax sourcetype=dellemc:vmax:rest reporting_level="Array"
    iseval=0

    [powermax_srp]
    definition = index=powermax sourcetype=dellemc:vmax:rest reporting_level="SRP"
    iseval=0

Once all the macros have been updated to reflect the indexes in use, save the
file and return to Splunk UI. It is advisable here to restart your Splunk
Enterprise server here so changes made here are applied.

Usage Considerations
--------------------
When using PowerMax for Splunk for performance metrics collection there are a
number of usage considerations that you should keep in mind:

- The PowerMax for Splunk TA is configured to run entirely from KPI metrics,
  if you do not need any further functionality from the TA and App other than
  to use the App for PowerMax monitoring then you only need to set each
  performance category to collect KPI metrics.
- If defining a list of custom metrics for a performance category, the format
  of those metrics should be in ``CamelCase`` exactly as they are in the
  Unisphere for PowerMax official documentation performance section.
- After enabling Unisphere for performance metrics collection allow Unisphere
  30 minutes to gather enough data before adding the array to Splunk as a data
  input.
- The most granular time available with Unisphere diagnostic performance
  metrics collection is 300 seconds, reporting intervals cannot be set lower
  than 300 seconds.
- If you are collecting metrics from multiple arrays it may take longer than
  300 seconds to complete an entire collection run. If this does happen
  you will see warning messages in your TA logs along with a recommendation
  on what interval should be set.
- If the Unisphere last available performance timestamp is not recent as of
  5-10 minutes ago there is a strong likelihood that your instance of Unisphere
  has gone into catch-up mode and is processing a backlog of performance data.
  It will resume normal operations once this backlog processing is complete.
- When querying a single instance of Unisphere for performance metrics across
  a multiple arrays be careful on the load placed on Unisphere, more arrays
  equates to more Unisphere REST API calls.

Lastly, and most importantly, *with great power comes great responsibility*.
PowerMax for Splunk provides you with the ability to query every performance
metric for a wide range of performance categories. It is important to
remember that the more assets you have created on an array, the more REST calls
that are required to collect information on all of those assets. Multiply that
by the interval set and it can quickly result in a very large volume of calls
to Unisphere.

Instead of gathering everything possible, be resourceful with your calls and
only query what is needed. This will ensure PowerMax for Splunk is performant
and helps reduce network load and the Unisphere for PowerMax user experience is
not negatively affected by excessive REST API calls. If you are only interested
in querying for KPIs, you can specify that only KPI metrics are returned,
but better still only query for a subset of metrics that you are interested in
if you do not require the full suite of dashboards available in the PowerMax
for Splunk App.

Where to find logs
------------------
If you are having issues with the TA or want to check on the performance of
metric collection runs you will need to look at the TA specific log file.
The default location for this log file is:

- ``{splunk_install_dir}/var/log/splunk/ta_dellemc_vmax_inputs.log``

The second important log is the ``splunkd`` log file. If there is issues
initialising the TA and nothing is appearing in the TA log, the ``splunkd``
logs may provide some answers. When Splunk is starting up there should be
warning or error messages for the TA indicating why there is initialisation
issues. The default location for this log file is:

- ``{splunk_install_dir}/var/log/splunk/splunkd.log``

Support Contact
---------------
In addition to contact via GitHub, it is possible to contact directly via
the support e-mail ``powermax.splunk.support@dell.com``. Please include as much
information as possible about the problem including:

- Detailed information about the problem you are having
- PowerMax for Splunk version
- Unisphere version
- Splunk Enterprise version
- Splunk Operating system version
- PowerMax for Splunk TA logs and splunkd logs if required


.. BadgeLinks

.. |Maintenance| image:: https://img.shields.io/badge/Maintained-Yes-blue
.. |OpenSource| image:: https://img.shields.io/badge/Open%20Source-Yes-blue
.. |AskUs| image:: https://img.shields.io/badge/Ask%20Us...-Anything-blue
.. |License| image:: https://img.shields.io/badge/License-Apache%202.0-blue
.. |Test| image:: https://img.shields.io/badge/Tests-Passing-blue
.. |Build| image:: https://img.shields.io/badge/Build-Passing-blue
.. |Docs| image:: https://img.shields.io/badge/Docs-Passing-blue
.. |Language| image:: https://img.shields.io/badge/Language-Python%20-blue
.. |PyVersions| image:: https://img.shields.io/badge/Python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9-blue
.. |Platform| image:: https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-blue
.. |Unisphere| image:: https://img.shields.io/badge/Unisphere-9.2.1.0-blue

.. URL LINKS

.. _ReadTheDocs: https://powermax-for-splunk.readthedocs.io/en/latest/overview.html
.. _PyU4V: https://github.com/dell/PyU4V
.. _`Dell EMC PowerMax Add-on for Splunk Enterprise`: https://splunkbase.splunk.com/app/3416/
.. _`Dell EMC PowerMax App for Splunk Enterprise`: https://splunkbase.splunk.com/app/3467/
.. _`Dell GitHub`: https://github.com/dell

