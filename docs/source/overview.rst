Overview
========

About the PowerMax for Splunk Add-on and App
--------------------------------------------
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


What's New in PowerMax for Splunk 3.0
-------------------------------------
- New categories have been added:

    - Masking View
    - IP Interface
    - iSCSI Target
    - Snapshot Policies
    - RDF Groups
    - Metro DR
    - Audit Logs

- The TA has been completely overhauled to integrate PyU4V to provide all
  required Unisphere for PowerMax REST API functionality.
- Users can now specify if they want to collect all metrics, key-performance
  indicator (KPI) metrics, or a custom set of metrics for each supported
  category in the PowerMax for Splunk TA.
- The now retired VMAX for Splunk sizer has been removed as a standalone
  script from the PowerMax for Splunk TA in favour of integrating its
  functionality directly into the TA. Now when a collection run exceeds the
  interval set for a given data input a warning message will appear in the
  logs along with a recommended interval to set.
- The TA has multiple code efficiency improvements to move to hash lookups over
  list iterations and use dictionaries and sets over lists where possible.
- The TA now has a full suite of unit tests and CI tests with full coverage of
  all code to improve reliability of submitted code and any future fixes.
- The TA now conforms to PEP8 and PyLint industry Python coding standards.
- The App has been redesigned so it will run entirely on KPI metrics. This is
  to cut down on the amount of data ingested into Splunk without impacting the
  functionality of the front end app.
- The App dashboard filter parameters are now bi-directional, they can be
  selected in any order and all other filter options will update accordingly to
  keep searches valid for your environment.
- The App dashboard charts have been set to use logarithmic scale on the y-axis
  instead of linear, this allows for better visualisation of results when there
  is a wide range on the y-axis.
- Documentation has had a complete redesign and is now also hosted on
  readthedocs.io.


Contact
-------
For all issues or queries please contact
``powermax.splunk.support@dell.com``. When contacting please include the
following information:

- Detailed information about the problem you are having
- PowerMax for Splunk version
- Unisphere version
- Splunk Enterprise version
- Splunk Operating system version
- PowerMax for Splunk TA logs and splunkd logs if required

Starting in PowerMax for Splunk 3.x you can open GitHub issues or discuss
topics related to PowerMax and Splunk. Feel free to open issues or topics if
this is your preferred method of communication. You can find out more support
information including where to get logs in :doc:`support`.


Hours of Operation
------------------
Working Hours - Ireland (GMT+00:00):

+-----------+---------------+
| Monday    | 08:00 - 16:30 |
+-----------+---------------+
| Tuesday   | 08:00 - 16:30 |
+-----------+---------------+
| Wednesday | 08:00 - 16:30 |
+-----------+---------------+
| Thursday  | 08:00 - 16:30 |
+-----------+---------------+
| Friday    | 08:00 - 15:30 |
+-----------+---------------+
| Saturday  | Closed        |
+-----------+---------------+
| Sunday    | Closed        |
+-----------+---------------+

Holidays Observed 2021:

+----------------------+---------------+
| New Year's Day       | 1st January   |
+----------------------+---------------+
| Saint Patrick's Day  | 17th March    |
+----------------------+---------------+
| Easter Monday        | 5th April     |
+----------------------+---------------+
| May Bank Holiday     | 3rd May       |
+----------------------+---------------+
| June Bank Holiday    | 7th June      |
+----------------------+---------------+
| August Bank Holiday  | 2nd August    |
+----------------------+---------------+
| October Bank Holiday | 25th October  |
+----------------------+---------------+
| Christmas Day        | 25th December |
+----------------------+---------------+
| Saint Stephen's Day  | 26th December |
+----------------------+---------------+

.. URL LINKS

.. _PyU4V: https://github.com/dell/PyU4V
.. _`Dell EMC PowerMax Add-on for Splunk Enterprise`: https://splunkbase.splunk.com/app/3416/
.. _`Dell EMC PowerMax App for Splunk Enterprise`: https://splunkbase.splunk.com/app/3467/
.. _`Dell EMC PowerMax Add-on for Splunk Enterprise source`: https://github.com/dell/powermax-splunk-addon
.. _`Dell EMC PowerMax App for Splunk Enterprise source`: https://github.com/dell/powermax-splunk-app
