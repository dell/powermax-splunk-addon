###########################################
# VMAX for Splunk Environment Sizer 2.0.1 #
# September 2018 - Michael McAleer        #
###########################################

Contact: vmax.splunk.support@emc.com

The VMAX for Splunk environment sizer helps to determine the optimum
reporting interval required for your VMAX inputs.

This sizer is meant to be used with one instance of Unisphere at a time, it is
not concerned with performance across multiple instances of Unisphere as this
would fall under the remit of Splunk performance.

This sizer will help set the VMAX for Splunk add-on input intervals so that
each input has enough time to complete before the reporting interval is exceeded
and metric collection intervals are missed.

Metrics collection run times depend entirely on your own environment, the VMAX
itself, how heavily utilised and loaded with resources it is etc, so there is no
one size fits all option. This script will simulate Splunk and gather summary
and performance metrics from an instance of Unisphere and VMAX(s) of your
choosing. These collection runs will also run concurrently as Splunk does. When
complete, information will be output as to how long metric collection lasted
for a given VMAX, and the recommended reporting interval time.

################
# Requirements #
################

-Python 2.7 (https://www.python.org/download/releases/2.7/)
-Requests (https://pypi.python.org/pypi/requests)

########################
# Instructions for use #
########################
1. Open the file 'vmax_splunk_sizer_config.ini' with a text editor of your choice
2. Under the heading [ENVIRONMENT_SETTINGS] set:
    2.1 Your Unisphere IP address or hostname
    2.2 Your Unisphere port (default is 8443)
    2.3 Your Unisphere username & password
    2.4 Your Unisphere SSL setup:
        2.4.1 If you require no SSL, set this to False
        2.4.2 If you have an SSL cert loaded into the system bundle, set this to
              True
        2.4.3 If you have an SSL cert but want to specify the path, set this to
              the path to SSL eg. /opt/splunk/certs/unisphere.pem
    2.5 Your VMAX numerical IDs, for more than one VMAX separate with a comma
3. Under [REPORTING_LEVELS], if you want to turn on or off any specific
   reporting level, change the value to False
4. Debug mode is not necessary unless diagnosing an issue with VMAX for Splunk
   support, but if you would like to see all calls output to screen, change
   this to true
5. To run the VMAX for Splunk environment sizer script just run the python
   file 'rest_vmax_splunk_sizer.py', there is no additional input required other
   than the configuration settings in 'vmax_splunk_sizer_config.ini'.