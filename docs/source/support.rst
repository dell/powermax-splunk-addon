Support
=======

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


GitHub Issues
-------------
From the PowerMax for Splunk 3.x release code will be hosted on the public
`Dell GitHub`_ repo. The code and documentation are released with no warranties
or SLAs and are intended to be supported through a community driven process.

We aim to track and document everything related to this repo via the issues
page. The following links will direct you to the issues sections of the
respective PowerMax for Splunk offerings:

- `PowerMax Add-on for Splunk Issues`_
- `PowerMax App for Splunk Issues`_

When opening an issue please include the following information to help us
debug:

- Detailed information about the problem you are having
- PowerMax for Splunk version
- Unisphere version
- Splunk Enterprise version
- Splunk Operating system version
- PowerMax for Splunk TA logs and splunkd logs if required (if these contain
  sensitive data they can be sent directly to our support contact alias listed
  in :ref:`Support:Support Contact`.

.. note::
    We will support N-2 releases from the current master release which includes
    bug and security fixes. If an issue appears in a code base older than N-2
    we will try to assist as best possible but ultimately upgrading to a newer
    version of PowerMax for Splunk will be the ideal outcome. As new releases
    of PowerMax for Splunk are made available, anything older than N-2 will be
    marked as End of Life (EOL).


GitHub Discussion
-----------------
A new feature in GitHub, 'Discussions', allows for community interaction
between developers and users. If you have a general query and would rather
community input for it than opening an issue or sending an e-mail to the
developers, Discussions is the place to do it.

- `PowerMax Add-on for Splunk Discussion`_
- `PowerMax App for Splunk Discussion`_

Before opening a new discussion, check if there are no existing discussions
that match what you would like to talk about.  If you cannot find an
existing discussion, open one and describe your topic as clearly as possible,
including TA/App versions where applicable.


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

.. URL LINKS

.. _issues: https://github.com/MichaelMcAleer/PyU4V/issues
.. _`Dell GitHub`: https://github.com/dell
.. _`PowerMax Add-on for Splunk Issues`: https://github.com/dell/powermax-splunk-addon/issues
.. _`PowerMax App for Splunk Issues`: https://github.com/dell/powermax-splunk-app/issues
.. _`PowerMax Add-on for Splunk Discussion`: https://github.com/dell/powermax-splunk-addon/discussions
.. _`PowerMax App for Splunk Discussion`: https://github.com/dell/powermax-splunk-app/discussions
