
# encoding = utf-8

import os
import sys
import time
import datetime

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''

def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # u4v_ip_address = definition.parameters.get('u4v_ip_address', None)
    # u4v_port = definition.parameters.get('u4v_port', None)
    # u4v_username = definition.parameters.get('u4v_username', None)
    # u4v_password = definition.parameters.get('u4v_password', None)
    # u4v_vmax_id = definition.parameters.get('u4v_vmax_id', None)
    # rest_request_timeout = definition.parameters.get('rest_request_timeout', None)
    # select_array = definition.parameters.get('select_array', None)
    # select_array_metrics = definition.parameters.get('select_array_metrics', None)
    # select_srp = definition.parameters.get('select_srp', None)
    # select_srp_metrics = definition.parameters.get('select_srp_metrics', None)
    # select_sg = definition.parameters.get('select_sg', None)
    # select_sg_metrics = definition.parameters.get('select_sg_metrics', None)
    # select_director = definition.parameters.get('select_director', None)
    # select_fe_dir_metrics = definition.parameters.get('select_fe_dir_metrics', None)
    # select_be_dir_metrics = definition.parameters.get('select_be_dir_metrics', None)
    # select_rdf_dir_metrics = definition.parameters.get('select_rdf_dir_metrics', None)
    # select_im_dir_metrics = definition.parameters.get('select_im_dir_metrics', None)
    # select_eds_dir_metrics = definition.parameters.get('select_eds_dir_metrics', None)
    # select_em_dir_metrics = definition.parameters.get('select_em_dir_metrics', None)
    # select_port = definition.parameters.get('select_port', None)
    # select_fe_port_metrics = definition.parameters.get('select_fe_port_metrics', None)
    # select_be_port_metrics = definition.parameters.get('select_be_port_metrics', None)
    # select_rdf_port_metrics = definition.parameters.get('select_rdf_port_metrics', None)
    # select_pg = definition.parameters.get('select_pg', None)
    # select_pg_metrics = definition.parameters.get('select_pg_metrics', None)
    # select_iscsi = definition.parameters.get('select_iscsi', None)
    # select_ip_interface_metrics = definition.parameters.get('select_ip_interface_metrics', None)
    # select_iscsi_target_metrics = definition.parameters.get('select_iscsi_target_metrics', None)
    # select_host = definition.parameters.get('select_host', None)
    # select_host_metrics = definition.parameters.get('select_host_metrics', None)
    # select_mv = definition.parameters.get('select_mv', None)
    # select_mv_metrics = definition.parameters.get('select_mv_metrics', None)
    # select_initiator = definition.parameters.get('select_initiator', None)
    # select_initiator_metrics = definition.parameters.get('select_initiator_metrics', None)
    # select_rdf = definition.parameters.get('select_rdf', None)
    # select_rdfs_metrics = definition.parameters.get('select_rdfs_metrics', None)
    # select_rdfa_metrics = definition.parameters.get('select_rdfa_metrics', None)
    # select_metro_dr = definition.parameters.get('select_metro_dr', None)
    # select_snap_policy = definition.parameters.get('select_snap_policy', None)
    # select_audit_logs = definition.parameters.get('select_audit_logs', None)
    # select_alerts = definition.parameters.get('select_alerts', None)
    pass

def collect_events(helper, ew):
    """Implement your data collection logic here

    # The following examples get the arguments of this input.
    # Note, for single instance mod input, args will be returned as a dict.
    # For multi instance mod input, args will be returned as a single value.
    opt_u4v_ip_address = helper.get_arg('u4v_ip_address')
    opt_u4v_port = helper.get_arg('u4v_port')
    opt_u4v_username = helper.get_arg('u4v_username')
    opt_u4v_password = helper.get_arg('u4v_password')
    opt_u4v_vmax_id = helper.get_arg('u4v_vmax_id')
    opt_rest_request_timeout = helper.get_arg('rest_request_timeout')
    opt_select_array = helper.get_arg('select_array')
    opt_select_array_metrics = helper.get_arg('select_array_metrics')
    opt_select_srp = helper.get_arg('select_srp')
    opt_select_srp_metrics = helper.get_arg('select_srp_metrics')
    opt_select_sg = helper.get_arg('select_sg')
    opt_select_sg_metrics = helper.get_arg('select_sg_metrics')
    opt_select_director = helper.get_arg('select_director')
    opt_select_fe_dir_metrics = helper.get_arg('select_fe_dir_metrics')
    opt_select_be_dir_metrics = helper.get_arg('select_be_dir_metrics')
    opt_select_rdf_dir_metrics = helper.get_arg('select_rdf_dir_metrics')
    opt_select_im_dir_metrics = helper.get_arg('select_im_dir_metrics')
    opt_select_eds_dir_metrics = helper.get_arg('select_eds_dir_metrics')
    opt_select_em_dir_metrics = helper.get_arg('select_em_dir_metrics')
    opt_select_port = helper.get_arg('select_port')
    opt_select_fe_port_metrics = helper.get_arg('select_fe_port_metrics')
    opt_select_be_port_metrics = helper.get_arg('select_be_port_metrics')
    opt_select_rdf_port_metrics = helper.get_arg('select_rdf_port_metrics')
    opt_select_pg = helper.get_arg('select_pg')
    opt_select_pg_metrics = helper.get_arg('select_pg_metrics')
    opt_select_iscsi = helper.get_arg('select_iscsi')
    opt_select_ip_interface_metrics = helper.get_arg('select_ip_interface_metrics')
    opt_select_iscsi_target_metrics = helper.get_arg('select_iscsi_target_metrics')
    opt_select_host = helper.get_arg('select_host')
    opt_select_host_metrics = helper.get_arg('select_host_metrics')
    opt_select_mv = helper.get_arg('select_mv')
    opt_select_mv_metrics = helper.get_arg('select_mv_metrics')
    opt_select_initiator = helper.get_arg('select_initiator')
    opt_select_initiator_metrics = helper.get_arg('select_initiator_metrics')
    opt_select_rdf = helper.get_arg('select_rdf')
    opt_select_rdfs_metrics = helper.get_arg('select_rdfs_metrics')
    opt_select_rdfa_metrics = helper.get_arg('select_rdfa_metrics')
    opt_select_metro_dr = helper.get_arg('select_metro_dr')
    opt_select_snap_policy = helper.get_arg('select_snap_policy')
    opt_select_audit_logs = helper.get_arg('select_audit_logs')
    opt_select_alerts = helper.get_arg('select_alerts')
    # In single instance mode, to get arguments of a particular input, use
    opt_u4v_ip_address = helper.get_arg('u4v_ip_address', stanza_name)
    opt_u4v_port = helper.get_arg('u4v_port', stanza_name)
    opt_u4v_username = helper.get_arg('u4v_username', stanza_name)
    opt_u4v_password = helper.get_arg('u4v_password', stanza_name)
    opt_u4v_vmax_id = helper.get_arg('u4v_vmax_id', stanza_name)
    opt_rest_request_timeout = helper.get_arg('rest_request_timeout', stanza_name)
    opt_select_array = helper.get_arg('select_array', stanza_name)
    opt_select_array_metrics = helper.get_arg('select_array_metrics', stanza_name)
    opt_select_srp = helper.get_arg('select_srp', stanza_name)
    opt_select_srp_metrics = helper.get_arg('select_srp_metrics', stanza_name)
    opt_select_sg = helper.get_arg('select_sg', stanza_name)
    opt_select_sg_metrics = helper.get_arg('select_sg_metrics', stanza_name)
    opt_select_director = helper.get_arg('select_director', stanza_name)
    opt_select_fe_dir_metrics = helper.get_arg('select_fe_dir_metrics', stanza_name)
    opt_select_be_dir_metrics = helper.get_arg('select_be_dir_metrics', stanza_name)
    opt_select_rdf_dir_metrics = helper.get_arg('select_rdf_dir_metrics', stanza_name)
    opt_select_im_dir_metrics = helper.get_arg('select_im_dir_metrics', stanza_name)
    opt_select_eds_dir_metrics = helper.get_arg('select_eds_dir_metrics', stanza_name)
    opt_select_em_dir_metrics = helper.get_arg('select_em_dir_metrics', stanza_name)
    opt_select_port = helper.get_arg('select_port', stanza_name)
    opt_select_fe_port_metrics = helper.get_arg('select_fe_port_metrics', stanza_name)
    opt_select_be_port_metrics = helper.get_arg('select_be_port_metrics', stanza_name)
    opt_select_rdf_port_metrics = helper.get_arg('select_rdf_port_metrics', stanza_name)
    opt_select_pg = helper.get_arg('select_pg', stanza_name)
    opt_select_pg_metrics = helper.get_arg('select_pg_metrics', stanza_name)
    opt_select_iscsi = helper.get_arg('select_iscsi', stanza_name)
    opt_select_ip_interface_metrics = helper.get_arg('select_ip_interface_metrics', stanza_name)
    opt_select_iscsi_target_metrics = helper.get_arg('select_iscsi_target_metrics', stanza_name)
    opt_select_host = helper.get_arg('select_host', stanza_name)
    opt_select_host_metrics = helper.get_arg('select_host_metrics', stanza_name)
    opt_select_mv = helper.get_arg('select_mv', stanza_name)
    opt_select_mv_metrics = helper.get_arg('select_mv_metrics', stanza_name)
    opt_select_initiator = helper.get_arg('select_initiator', stanza_name)
    opt_select_initiator_metrics = helper.get_arg('select_initiator_metrics', stanza_name)
    opt_select_rdf = helper.get_arg('select_rdf', stanza_name)
    opt_select_rdfs_metrics = helper.get_arg('select_rdfs_metrics', stanza_name)
    opt_select_rdfa_metrics = helper.get_arg('select_rdfa_metrics', stanza_name)
    opt_select_metro_dr = helper.get_arg('select_metro_dr', stanza_name)
    opt_select_snap_policy = helper.get_arg('select_snap_policy', stanza_name)
    opt_select_audit_logs = helper.get_arg('select_audit_logs', stanza_name)
    opt_select_alerts = helper.get_arg('select_alerts', stanza_name)

    # get input type
    helper.get_input_type()

    # The following examples get input stanzas.
    # get all detailed input stanzas
    helper.get_input_stanza()
    # get specific input stanza with stanza name
    helper.get_input_stanza(stanza_name)
    # get all stanza names
    helper.get_input_stanza_names()

    # The following examples get options from setup page configuration.
    # get the loglevel from the setup page
    loglevel = helper.get_log_level()
    # get proxy setting configuration
    proxy_settings = helper.get_proxy()
    # get account credentials as dictionary
    account = helper.get_user_credential_by_username("username")
    account = helper.get_user_credential_by_id("account id")
    # get global variable configuration
    global_userdefined_global_var = helper.get_global_setting("userdefined_global_var")

    # The following examples show usage of logging related helper functions.
    # write to the log for this modular input using configured global log level or INFO as default
    helper.log("log message")
    # write to the log using specified log level
    helper.log_debug("log message")
    helper.log_info("log message")
    helper.log_warning("log message")
    helper.log_error("log message")
    helper.log_critical("log message")
    # set the log level for this modular input
    # (log_level can be "debug", "info", "warning", "error" or "critical", case insensitive)
    helper.set_log_level(log_level)

    # The following examples send rest requests to some endpoint.
    response = helper.send_http_request(url, method, parameters=None, payload=None,
                                        headers=None, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=True)
    # get the response headers
    r_headers = response.headers
    # get the response body as text
    r_text = response.text
    # get response body as json. If the body text is not a json string, raise a ValueError
    r_json = response.json()
    # get response cookies
    r_cookies = response.cookies
    # get redirect history
    historical_responses = response.history
    # get response status code
    r_status = response.status_code
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()

    # The following examples show usage of check pointing related helper functions.
    # save checkpoint
    helper.save_check_point(key, state)
    # delete checkpoint
    helper.delete_check_point(key)
    # get checkpoint
    state = helper.get_check_point(key)

    # To create a splunk event
    helper.new_event(data, time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    """

    '''
    # The following example writes a random number as an event. (Multi Instance Mode)
    # Use this code template by default.
    import random
    data = str(random.randint(0,100))
    event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=data)
    ew.write_event(event)
    '''

    '''
    # The following example writes a random number as an event for each input config. (Single Instance Mode)
    # For advanced users, if you want to create single instance mod input, please use this code template.
    # Also, you need to uncomment use_single_instance_mode() above.
    import random
    input_type = helper.get_input_type()
    for stanza_name in helper.get_input_stanza_names():
        data = str(random.randint(0,100))
        event = helper.new_event(source=input_type, index=helper.get_output_index(stanza_name), sourcetype=helper.get_sourcetype(stanza_name), data=data)
        ew.write_event(event)
    '''
