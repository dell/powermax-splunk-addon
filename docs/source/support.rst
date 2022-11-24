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

Support Contact
---------------
Contact directly via the support e-mail ``powermax.splunk.support@dell.com``. Please include as much
information as possible about the problem including:

- Detailed information about the problem you are having
- PowerMax for Splunk version
- Unisphere version
- Splunk Enterprise version
- Splunk Operating system version
- PowerMax for Splunk TA logs and splunkd logs if required

.. URL LINKS

.. _`Dell GitHub`: https://github.com/dell
