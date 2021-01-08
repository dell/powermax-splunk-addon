###############
# Information #
###############
-Title: Dell EMC VMAX/PowerMax Add-on for Splunk Enterprise
-Add-on Version: 2.0.9
-Document Version: 2.0.0
-Date: 4th September 2020
-Vendor Products: Dell EMC VMAX3 and PowerMax
-Visible in Splunk Web: Yes. This add-on contains set-up configuration options.


###########
# Contact #
###########
For any and all issues or queries, please contact vmax.splunk.support@emc.com.
Include as much information as possible about the issue, the Operating System
and Splunk versions, and associated log files listed in the troubleshooting
section.

• Response Time: Within 48hrs
• How we track issues: Internal Bug tracking system


##################################################
# Hours of Operation & Holidays Observed 2019/20 #
##################################################
All times are specific to Ireland (GMT+00:00)

Working Hours:
    Monday      : 09:00 - 17:00
    Tuesday     : 09:00 - 17:00
    Wednesday   : 09:00 - 17:00
    Thursday    : 09:00 - 17:00
    Friday      : 09:00 - 16:00
    Saturday    : Closed
    Sunday      : Closed

Holidays Observed 2020/21:
Date	       Holiday Name
26 Oct 20      October bank holiday
25 Dec 20      Christmas day
26 Dec 20      St. Stephen's day
1 Jan 21       New Year's day
17 Mar 21      St. Patrick's day
7 Jun 21       June bank holiday
2 Aug 21       August bank holiday
25 Oct 21      October bank holiday
25 Dec 21      Christmas day
26 Dec 21      St. Stephen's day


###############################################
# About the VMAX Add-on for Splunk Enterprise #
###############################################
The Splunk Technology Add-on (TA) for Dell EMC VMAX/PowerMax allows a Splunk®
Enterprise administrator to collect inventory, performance information, and
summary information from VMAX/PowerMax storage arrays. You can then directly
analyse the data or use it as a contextual data feed to correlate with other
operational or security data in Splunk Enterprise.

The Splunk VMAX/PowerMax TA is configured to report events in 5 minute
intervals which is the lowest possible granularity for performance metrics
reporting. Event metric values are representative of the value recorded at that
point in time on the VMAX/PowerMax. Values shown for an event in Splunk at
10:00am represent their respective values at 10:00am on the VMAX/PowerMax.

Download the Splunk Add-on for Dell EMC VMAX/PowerMax from Splunkbase.


#################
# Release Notes #
#################
Version 2.0.9 of the VMAX/PowerMax TA is compatible with:
    -Splunk Platform: 8.0 and above
    -CIM: 4.6 and above
    -OS Platforms: Splunk compatible platforms
    -Vendor Hardware: Dell EMC VMAX3, VMAX All-Flash, and PowerMax
    -Vendor Software: Solutions Enabler 9.0 and newer
                      Unisphere for PowerMax 9.0 and newer

Note: Workload Planner headroom information is not supported in Splunk with
Unisphere 9.1, to retain this functionality please use Unisphere 9.0.


###############################################
# PowerMax TA Requirements and Considerations #
###############################################
-Splunk Administrator Requirements
To install and configure the Splunk PowerMax TA, you must have admin privileges.

-Hardware & Software
As this add-on runs on Splunk Enterprise, all Splunk Enterprise system
requirements apply. Dell EMC VMAX-3 Series and PowerMax arrays are supported by
the TA. Solutions Enabler 9.0 or newer and Unisphere for PowerMax 9.0
and newer are required.

-Additional Recommendations
The add-on does not require the ability to modify VMAX/PowerMax configuration.
It is highly recommended that you create a read-only user account for Splunk in
Unisphere for PowerMax.

Before any metrics can be collected from an array you must also ensure that the
VMAX/PowerMax is registered to collect performance metrics. This is enabled
from within the PowerMax for VMAX Web UI. For more information see the section
‘Enabling Performance Metrics Collection’ below.

Performance of data collection is dependent on many factors, such as
VMAX/PowerMax system load, Splunk Enterprise system load, and environmental
factors such as network latency. Performance considerations are discussed in
the section ‘Running Sizer’ and how to mitigate these in your environment
for best possible performance from metric collections.


###########################################
# Enabling Performance Metrics Collection #
###########################################
To enable Splunk to gather performance data on the array(s) in your
environment it is necessary to first enable performance metrics for the given
array(s) by registering the system to collect performance data. To register
your array(s) follow these steps:

1. Log in to Unisphere and navigate to Settings > Performance > System
Registrations

2. Beside 'All' click the arrow to reveal the local arrays to that instance of
Unisphere.

3. For each array that you want to register for performance metrics check the
box under 'Diagnostic'.

6. With the registration process complete, leave Unisphere for 2-4hrs to start
gathering performance metrics before adding the array to Splunk. Performance
metrics collection is not immediate, for more information please refer to the
‘Performance Management – Metrics’ section of the ‘Unisphere 9.1 Online Help’
guide available on support.emc.com


###################################################################################
# Installation and configuration overview for the Splunk Add-on for VMAX/PowerMax #
###################################################################################
As there are no dependencies required for the installation of the Splunk Add-on
for VMAX/PowerMax, the set-up is completed entirely from within the Splunk web
UI.

1. From your Splunk home screen, click the cog icon beside ‘Apps’ to navigate
to the ‘Manage Apps’ section.

2. Within the ‘Manage Apps’ section, click the button ‘Install App from file’.

3. Click ‘Choose File’, select the VMAX Add-on for Splunk, and click ‘Upload’.

4. Once the upload is complete you will be prompted to restart Splunk to
complete the installation, click ‘Restart now’. When Splunk restarts, navigate
back to the home screen and you will now see a dashboard panel for the VMAX TA.
Click on the panel to start adding your array(s) to Splunk.

5. Once opened, you can add array(s) to Splunk by clicking on the ‘Create New
Input’ button in the top right of the UI.

6. To add an array to Splunk, you must enter a number of details into Splunk
about the instance of Unisphere used, array details, SSL details, and reporting
metrics configuration. The table below lists each option, its default value if
there is one, and a description of the option. Once all options are set, click
‘Add’ to add the VMAX as a data input to Splunk. A breakdown of all options can
be found below:

Input 	                    Default	    Description
Name	                    None	    The name of the input as is will appear
                                        in Splunk
Interval	                300	        The metrics collection interval. This
                                        should be set in increments of 300s as
                                        this is the reporting interval of
                                        performance metrics in Unisphere. For
                                        more information on determining the
                                        ideal setting for the reporting interval
                                        for your environment, see the ‘VMAX for
                                        Splunk Sizer’ section below.
Index	                    Default	    The index to which data from Unisphere
                                        for this VMAX will be written.
Unisphere IP Address	    None	    Unisphere IP address or hostname.
Unisphere Port	            8443	    Unisphere port.
Unisphere Username	        None	    Unisphere username.
Unisphere Password	        None	    Unisphere password.
VMAX Numerical ID	        None	    The 12-digit numerical VMAX ID
Enable SSL	                True	    If you require end-to-end SSL
                                        communication between Splunk and
                                        Unisphere. Uncheck to disable SSL
                                        entirely. See ‘SSL Configuration’
                                        section below for more information on
                                        SSL set-up.
SSL Cert Location	        None	    If ‘Enable SSL’ is enabled, this option
                                        has two behaviours:
                                        1.	If left blank, Splunk will search
                                        the system certs bundle for a valid
                                        Unisphere cert.
                                        2.	If a path is provided, this is the
                                        path Splunk will use to access the
                                        Unisphere cert independently of the
                                        system certs bundle.
REST Request Timeout	    60	        The amount of time Splunk will wait for
                                        a response from Unisphere for any given
                                        call before timing out and logging an
                                        error. If changing from default,
                                        consider Unisphere load, setting it too
                                        low may have a negative impact on
                                        metrics collection.
Array	                    True	    Collect array level metrics.
Alerts	                    True	    Collect VMAX system alerts.
Collect VMAX only metrics	False	    If enabled, Splunk will collect only
                                        those metrics which directly specify the
                                        Array ID in the alert description (see
                                        known issues section for impact of
                                        enabling this option). If disabled,
                                        Splunk will gather all system alerts
                                        from the instance of Unisphere it is
                                        collecting VMAX metrics from, even for
                                        those VMAXs which are not added as an
                                        input to Splunk.
Storage Resource Pool	    True	    Collect Storage Resource Pool metrics.
Storage Group	            True	    Collect Storage Group metrics.
Director	                True	    Collect Director metrics.
Port	                    True	    Collect Port metrics.
Port Group	                True	    Collect Port Group metrics.
Host	                    True	    Collect Host metrics.
Initiator	                True	    Collect Initiator metrics.
Workload Planner	        True	    Collect Workload Compliance & Headroom
                                        metrics.

7. To add another array to the TA, repeat steps 5-6 as many times as necessary.

8. When all array(s) have been added to the TA, you will see them listed within
the TA. From here you can enable, disable, or edit the options for a given
array after it has been configured.

9. Once an array has been added to the TA, it starts gathering information
immediately. To access that data, use Splunk Search to start looking at
VMAX/PowerMax related events using the SPL query:
sourcetype="dellemc:vmax:rest”


#####################
# SSL Configuration #
#####################
SSL is enabled by default in the TA when adding inputs. In order to
retrieve the required certificate from Unisphere follow the following steps:

1. Get the CA certificate of the Unisphere server. This pulls the CA cert file
and saves it as .pem file:

# openssl s_client -showcerts -connect {unisphere_host}:8443 </dev/null 2> \
/dev/null|openssl x509 -outform PEM >{unisphere_host}.pem

Where {unisphere_host} is the IP address or hostname of the Unisphere instance.

2. OPTIONAL: If you want to add the cert to the system certificate bundle so no
certificate path is specified in the VMAX data input, copy the .pem file to the
system certificate directory as a .crt file:

# {unisphere_host}.pem /usr/share/ca-certificates/{unisphere_host}.crt

3. OPTIONAL: Update CA certificate database with the following commands:

# dpkg-reconfigure ca-certificates
# update-ca-certificates

Check that the new {unisphere_host}.crt will activate by selecting ask on the
dialog. If it is not enabled for activation, use the down and up keys to select,
and the space key to enable or disable.

4. If steps 2 & 3 are skipped and instead the cert from step 1 will just remain
in a local directory, you can specify the location of the .pem cert in the VMAX
data input setting 'SSL Cert Location'. Otherwise, leave ‘SSL Cert Location’
blank and ‘Enable SSL’ enabled to use the cert from the system certificate
bundle.


##################################
# VMAX/PowerMax for Splunk Sizer #
##################################
An additional script has been included with the TA to help determine the
optimum reporting interval required for your data inputs.

This sizer is meant to be used with one instance of Unisphere at a time, it is
not concerned with performance across multiple instances of Unisphere as this
would fall under the remit of Splunk performance.

This sizer will help set the TA input intervals so that each input has enough
time to complete before the reporting interval is exceeded and metric
collection intervals are missed.

Metrics collection run times depend entirely on the environment, the
VMAX/PowerMax itself, how heavily utilised and loaded with resources it is, so
there is no one size fits all option. This script will simulate Splunk and
gather summary and performance metrics from an instance of Unisphere and
array(s) of your choosing. These collection runs will also run concurrently as
Splunk does. When complete, information will be output as to how long metric
collection lasted for a given array, and the recommended reporting interval
time.

To run VMAX for Splunk sizer script, you will require Python 3.6 or newer and
the Python Requests library:
•	Requests - https://pypi.python.org/pypi/requests

To run the sizer script, follow the steps below:

1. Navigate to the TA folder containing the sizer script and configuration
file:

# cd {splunk_dir}/etc/apps/TA-DellEMC-VMAX/bin/sizer

2. Open the vmax_splunk_sizer_config.ini configuration file for editing.

3. Under [ENVIRONMENT_SETTINGS] set:
    •	The Unisphere IP address or hostname
    •	The Unisphere port (default is 8443)
    •	The Unisphere username & password
    •	The required SSL setup:
        o	If you require no SSL, set this to False
        o	If you have an SSL cert loaded into the system bundle, set this to
            True
        o	If you have an SSL cert but want to specify the path, set this to
            the path to the cert
    •	Your array numerical IDs, for more than one array separate with a comma

4. Under [REPORTING_LEVELS], if you want to turn on or off any specific
reporting level change the value to False

5. Debug mode is not necessary unless diagnosing an issue with VMAX for Splunk
support, but if you would like to see all calls output to screen, change this
to True

5. With all the environment settings configured, run the VMAX for Splunk
environment sizer script using the python file 'rest_vmax_splunk_sizer.py'

$ python3 rest_vmax_splunk_sizer.py

6. Once the script has run to completion, details of the metrics collection run
will be output to the screen along with recommendations on the optimum reporting
interval for each array.


#######################################################
# Source Type for the VMAX/PowerMax Add-on for Splunk #
#######################################################
The TA provides the index-time and search-time knowledge for inventory,
performance metrics, and summary information. By default, all array data is
indexed into the default Splunk index, this is the ‘main’ index unless changed
by the admin.

The source type used for the Splunk Add-on for VMAX/PowerMax is
dellemc:vmax:rest. All events are in key/value pair formats. All events have an
assigned 'reporting_level' which indicates the level at which the event
details, along with the associated array ID & if reporting at lower levels,
the object ID e.g. Storage Group, Director, Host.

The add-on collects many different kinds of events for VMAX/PowerMax, including
performance, inventory, and summary metrics. Depending on the activity of the
Port Groups & Initiators in your environment, there may be events where there
are no performance metrics collected. This can be confirmed if there is a metric
present in the event named {reporting_level}_perf_details with a value of False
(where reporting_level is the reporting level of the event itself). For more
information see the section ‘Active vs. Inactive Object Performance Reporting’.


####################################################
# Active vs. Inactive Object Performance Reporting #
####################################################
To limit the amount of data collected and stored on an array, only active Port
Groups, Hosts, and Initiators are reported against for performance metrics.
Inactivity is determined by no activity being recorded by performance monitors
for a specified amount of time. The VMAX ingests a wide range of metrics
across each of the reporting levels. To get detailed definitions of each of the
performance metrics see the ‘Performance Management’ section of the
‘Unisphere 9.1 Online Help’ guide available on support.emc.com

This is not enforced by Splunk but is the behaviour of the VMAX/PowerMax,
recording zero values for every Port Group, Host, and Initiator in an
environment would very quickly fill databases with useless data.

When the TA is collecting information on the Port Groups, Hosts, or
Initiators in your environment, it will first obtain a list of all objects for
each reporting level. Using this list, calls will be to Unisphere for
performance metrics for each, if an object is inactive, no performance metrics
will be returned. This inactivity is reflected in the array events through the
key/value pairs below.

{reporting_level}_perf_details: false
{reporting_level}_perf_message: No active {reporting_level} performance data
                                available


#######################################################
# Troubleshooting the VMAX/PowerMax Add-on for Splunk #
#######################################################
The Splunk VMAX/PowerMax TA has been developed to give the end-user as much
detail as possible about the activity of the add-on in their environment. All
add-on logged events will either be marked as info, error, or critical
depending on the nature of the event. If you are having any issues with the
add-on, the logs will be able to give you precise information as to the cause
of the problem. These issues could be related, but not limited to:

•	Incorrect Unisphere configuration or username/password combination
•	Incorrect SSL setup
•	Incorrect Array ID
•	VMAX/PowerMax is not performance registered
•	Performance metrics timestamp is not up-to-date

The two log files that you can use to diagnose problems with this add-on are:
•	/{splunk_install_dir}/splunk/var/log/splunk/ta_dellemc_vmax_inputs.log
•	/{splunk_install_dir}/splunk/var/log/splunk/splunkd.log

Before the add-on successfully runs for the first time, error logs go to
splunkd.log. After the add-on successfully runs, error logs go to
ta_dellemc_vmax_inputs.log.


###################################
# Performance Metrics Definitions #
###################################
The TA ingests a wide range of metrics across each of the reporting levels.
To get detailed definitions of each of the performance metrics see the
‘Performance Management – Metrics’ section of the ‘Unisphere 9.1 Online Help’
guide available on support.emc.com


################
# Known Issues #
################
-Workload Planner Headroom
Workload Planner Headroom data will not be extracted from Unisphere for
PowerMax 9.1 for use in Splunk in version 2.0.9 of the TA. A substantial amount
of work was carried out on the Unisphere Workload Planner REST endpoints in
verison 9.1, to port existing TA calls over to these new endpoints would be
a substantial amount of work to cover three major Unisphere releases. To retain
Workload Planner Headroom statistics ingestion please use Unisphere for
PowerMax 9.0.  This problem will be resolved in the next major VMAX/PowerMax
for SplunkTA release.

-VMAX Alerts
When requesting VMAX alert information from the Unisphere REST API through the
/system/alert endpoints there is no key/value pairs for the array and object ID.
When the event is processed in the VMAX TA, the alert description is parsed and
if an array or object ID is present, it is added before the data is indexed in
Splunk. At present, most information can be parsed from the description but this
does not always work.

An example of not being able to parse the array/object info from an alert is
with array metadata usage. Using the REST API there is no IDs associated with
the alert so unless the user reverts to Unisphere manually there is no way they
can know what array the alert belongs to.

The impact of this in the VMAX TA is that when ‘Collect VMAX only metrics’ is
enabled, certain alerts which do not have the array/object info in the alert
description will not be ingested into Splunk. This is because this option uses
the array ID key/value pair to determine if it is related to the VMAX ID
specified in the data input.

It must be noted however, that the data for which the alert describes can be
viewed within the various dashboards of the VMAX App for Splunk. For example,
the array metadata usage percentage is featured as a time chart in the VMAX
dashboard. This is because for each of the reporting levels, every possible
piece of information pertaining to each reporting levels’ objects is retrieved
from Unisphere.

If ‘Collect VMAX only metrics’ is left disabled, all system alerts from the
instance of Unisphere specified in the VMAX data input will be ingested into
Splunk. This also means that any system alerts for other arrays which are not
added as data inputs, but present in that instance of Unisphere associated with
the data input are ingested into Splunk.

-REST Response Code 401
Occasionally when the Unisphere REST API is under heavy load of REST requests it
may return a 401 response to a request from the VMAX TA. This is temporary and
will clear itself, usually immediately.


###########
# Contact #
###########
For any and all issues or queries, please contact vmax.splunk.support@emc.com.
Include as much information as possible about the issue, the Operating System
and Splunk versions, and associated log files listed in the troubleshooting
section.
