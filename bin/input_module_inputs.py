# encoding = utf-8
from rest_functions import RestFunctions


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza
    configurations"""
    u4v_vmax_id = definition.parameters.get('u4v_vmax_id')
    interval = definition.parameters.get('interval')
    helper.log_info("Array: %(array)s - Running Splunk validation." % {
        'array': u4v_vmax_id})

    if int(interval) % 300 != 0:
        helper.log_info("Array: %(array)s - Interval must be divisible "
                        "by 300." % {'array': u4v_vmax_id})
        raise ValueError("Interval must be divisible by lowest possible "
                         "granularity of 300s.")
    else:
        helper.log_info("Array: %(array)s - Passed interval check." % {
            'array': u4v_vmax_id})
        pass


def collect_events(helper, ew):
    """Implement your data collection logic here"""
    # Environment Variables
    helper.set_log_level("INFO")
    spl_sourcetype = helper.get_sourcetype()
    spl_index = helper.get_output_index()
    u4v_ip_address = helper.get_arg('u4v_ip_address')
    u4v_port = helper.get_arg('u4v_port')
    u4v_username = helper.get_arg('u4v_username')
    u4v_password = helper.get_arg('u4v_password')
    u4v_vmax_id = helper.get_arg('u4v_vmax_id')
    u4v_rest_timeout = helper.get_arg('rest_request_timeout')
    u4v_source = ("vmax://%(u4v_ip_address)s::%(u4v_vmax_id)s" % {
        'u4v_ip_address': u4v_ip_address,
        'u4v_vmax_id': u4v_vmax_id})

    # SSL Setting
    enable_ssl = helper.get_arg('enable_ssl')
    ssl_cert_location = helper.get_arg('ssl_cert_location')
    ssl_verify = True
    if enable_ssl and ssl_cert_location:
        ssl_verify = ssl_cert_location
    elif not enable_ssl:
        ssl_verify = False

    # Metrics collection levels
    select_array = helper.get_arg('select_array')
    select_alerts = helper.get_arg('select_alerts')
    select_srp = helper.get_arg('select_srp')
    select_sg = helper.get_arg('select_sg')
    select_director = helper.get_arg('select_director')
    select_port = helper.get_arg('select_port')
    select_pg = helper.get_arg('select_pg')
    select_host = helper.get_arg('select_host')
    select_initiator = helper.get_arg('select_initiator')
    select_wlp = helper.get_arg('select_wlp')

    rf = RestFunctions(username=u4v_username, password=u4v_password,
                       server_ip=u4v_ip_address, port=u4v_port,
                       verify=ssl_verify, array=u4v_vmax_id,
                       rest_timeout=u4v_rest_timeout, helper=helper)

    if rf.valid:
        # Get Array level metrics
        if select_array:
            try:
                array_response = rf.get_array_summary(u4v_vmax_id)
                array_event = helper.new_event(source=u4v_source,
                                               index=spl_index,
                                               sourcetype=spl_sourcetype,
                                               data=array_response)
                ew.write_event(array_event)
                helper.log_info(
                    "Array: %(array)s - Array metrics collected." % {
                        'array': u4v_vmax_id})
            except TypeError:
                helper.log_error(
                    "Array: %(array)s - There was an issue collecting "
                    "Array level metrics, please check status code for "
                    "further information. This may be a temporary Unisphere "
                    "response error which will clear itself." % {
                        'array': u4v_vmax_id})

        # Get Alert info
        if select_alerts:
            try:
                symm_only_alerts = helper.get_arg('select_vmax_only_metrics')
                for alert in rf.get_alert_list(symm_only=symm_only_alerts):
                    try:
                        alert_response = rf.get_symm_alert_details(alert)
                        alert_event = helper.new_event(
                            source=u4v_source, index=spl_index,
                            sourcetype=spl_sourcetype, data=alert_response)
                        ew.write_event(alert_event)
                    except TypeError:
                        helper.log_error(
                            "Array: %(array)s Alert: %(alert)s - There was an "
                            "issue collecting Alert metrics, please check "
                            "status code for further information. This may be "
                            "a temporary Unisphere response error which will "
                            "clear itself." % {
                                'array': u4v_vmax_id,
                                'alert': alert})
            except TypeError:
                helper.log_error(
                    "Array: %(array)s - There was an issue collecting the "
                    "Alert ID list, please check status code for further "
                    "information. This may be a temporary Unisphere response "
                    "error which will clear itself." % {'array': u4v_vmax_id})

            helper.log_info("Array: %(array)s - Alerts info collected." % {
                'array': u4v_vmax_id})

        # Get SRP info
        if select_srp:
            try:
                for srp in rf.get_srp_list():
                    try:
                        srp_response = rf.get_srp_details(srp)
                        srp_event = helper.new_event(source=u4v_source,
                                                     index=spl_index,
                                                     sourcetype=spl_sourcetype,
                                                     data=srp_response)
                        ew.write_event(srp_event)
                    except TypeError:
                        helper.log_error(
                            "Array: %(array)s SRP: %(srp)s - There was an "
                            "issue collecting SRP metrics, please check "
                            "status code for further information. This may be "
                            "a temporary Unisphere response error which will "
                            "clear itself." % {
                                'array': u4v_vmax_id,
                                'srp': srp})
            except TypeError:
                helper.log_error(
                    "Array: %(array)s - There was an issue collecting the SRP "
                    "ID list, please check status code for further "
                    "information. This may be a temporary Unisphere response "
                    "error which will clear itself." % {'array': u4v_vmax_id})

            helper.log_info("Array: %(array)s - SRP level metrics collected."
                            % {'array': u4v_vmax_id})

        # Get SG info
        if select_sg:
            try:
                for sg in rf.get_sg_list():
                    try:
                        sg_response = rf.get_sg_details(sg)
                        sg_event = helper.new_event(source=u4v_source,
                                                    index=spl_index,
                                                    sourcetype=spl_sourcetype,
                                                    data=sg_response)
                        ew.write_event(sg_event)
                    except TypeError:
                        helper.log_error(
                            "Array: %(array)s SG: %(sg)s - There was an issue "
                            "collecting SG metrics, please check status code "
                            "for further information. This may be a temporary "
                            "Unisphere response error which will clear "
                            "itself." % {
                                'array': u4v_vmax_id,
                                'sg': sg})
            except TypeError:
                helper.log_error(
                    "Array: %(array)s - There was an issue collecting the SG "
                    "ID list, please check status code for further "
                    "information. This may be a temporary Unisphere response "
                    "error which will clear itself." % {'array': u4v_vmax_id})

            helper.log_info(
                "Array: %(array)s - SG level metrics collected." % {
                    'array': u4v_vmax_id})

        # Get Director info
        if select_director:
            try:
                for vmax_dir in rf.get_director_list():
                    try:
                        dir_response = rf.get_director_details(vmax_dir)
                        dir_event = helper.new_event(source=u4v_source,
                                                     index=spl_index,
                                                     sourcetype=spl_sourcetype,
                                                     data=dir_response)
                        ew.write_event(dir_event)
                    except TypeError:
                        helper.log_error(
                            "Array: %(array)s Director: %(vmax_dir)s - There "
                            "was an issue collecting Director metrics, please "
                            "check status code for further information. This "
                            "may be a temporary Unisphere response error "
                            "which will clear itself." % {
                                'array': u4v_vmax_id,
                                'vmax_dir': vmax_dir})
            except TypeError:
                helper.log_error(
                    "Array: %(array)s - There was an issue collecting the "
                    "Director ID list, please check status code for further "
                    "information. This may be a temporary Unisphere response "
                    "error which will clear itself." % {'array': u4v_vmax_id})

            helper.log_info("Array: %(array)s - Director level metrics "
                            "collected." % {'array': u4v_vmax_id})

        # Get Port info
        if select_port:
            try:
                for port in rf.get_port_list():
                    try:
                        port_response = rf.get_port_details(port)
                        port_event = helper.new_event(
                            source=u4v_source, index=spl_index,
                            sourcetype=spl_sourcetype, data=port_response)
                        ew.write_event(port_event)
                    except TypeError:
                        helper.log_error(
                            "Array: %(array)s Port: %(port)s - There was an "
                            "issue collecting Port metrics, please check "
                            "status code for further information. This may be "
                            "a temporary Unisphere response error which will "
                            "clear itself." % {
                                'array': u4v_vmax_id,
                                'port': port})
            except TypeError:
                helper.log_error(
                    "Array: %(array)s - There was an issue collecting the "
                    "Port ID list, please check status code for further "
                    "information. This may be a temporary Unisphere response "
                    "error which will clear itself." % {'array': u4v_vmax_id})

            helper.log_info(
                "Array: %(array)s - Port level metrics collected." %
                {'array': u4v_vmax_id})

        # Get Port Group Info
        if select_pg:
            try:
                for pg in rf.get_pg_list():
                    try:
                        pg_response = rf.get_pg_details(pg)
                        pg_event = helper.new_event(source=u4v_source,
                                                    index=spl_index,
                                                    sourcetype=spl_sourcetype,
                                                    data=pg_response)
                        ew.write_event(pg_event)
                    except TypeError:
                        dir_port = ("Dir:Port: %(dir)s:%(port)s" % {
                            'dir': pg['directorId'],
                            'port': pg['portId']
                        })
                        helper.log_error(
                            "Array: %(array)s PG: %(dir_port)s - There was an "
                            "issue collecting PG metrics, please check status "
                            "code for further information. This may be a "
                            "temporary Unisphere response error which will "
                            "clear itself." % {
                                'array': u4v_vmax_id,
                                'dir_port': dir_port})

            except TypeError:
                helper.log_error(
                    "Array: %(array)s - There was an issue collecting the "
                    "Port Group ID list, please check status code for "
                    "further information. This may be a temporary Unisphere "
                    "response error which will clear itself." % {
                        'array': u4v_vmax_id})

            helper.log_info("Array: %(array)s - PG level metrics collected" % {
                'array': u4v_vmax_id})

        # Get Host info
        if select_host:
            try:
                summary_hosts, active_hosts = rf.get_host_list()
                for host in summary_hosts:
                    try:
                        host_response = rf.get_host_details(host, active_hosts)
                        host_event = helper.new_event(
                            source=u4v_source, index=spl_index,
                            sourcetype=spl_sourcetype, data=host_response)
                        ew.write_event(host_event)
                    except TypeError:
                        helper.log_error(
                            "Array: %(array)s Host: %(host)s - There was an "
                            "issue collecting Host metrics, please check "
                            "status code for further information. This may be "
                            "a temporary Unisphere response error which will "
                            "clear itself." % {
                                'array': u4v_vmax_id,
                                'host': host})
            except TypeError:
                helper.log_error(
                    "Array: %(array)s - There was an issue collecting the "
                    "Host ID list, please check status code for further "
                    "information. This may be a temporary Unisphere response "
                    "error which will clear itself." % {'array': u4v_vmax_id})

            helper.log_info(
                "Array: %(array)s - Host level metrics collected." %
                {'array': u4v_vmax_id})

        # Get Initiator info
        if select_initiator:
            try:
                summary_inits, active_inits = rf.get_initiator_list()
                for initiator in summary_inits:
                    try:
                        initiator_response = rf.get_initiator_details(
                            initiator, active_inits)
                        initiator_event = helper.new_event(
                            source=u4v_source, index=spl_index,
                            sourcetype=spl_sourcetype, data=initiator_response)
                        ew.write_event(initiator_event)
                    except TypeError:
                        helper.log_error(
                            "Array: %(array)s Initiator: %(initiator)s - "
                            "There was an issue collecting Initiator metrics, "
                            "please check status code for further "
                            "information. This may be a temporary Unisphere "
                            "response error which will clear itself." % {
                                'array': u4v_vmax_id,
                                'initiator': initiator})
            except TypeError:
                helper.log_error(
                    "Array: %(array)s - There was an issue collecting the "
                    "Initiator ID list, please check status code for further "
                    "information. This may be a temporary Unisphere response "
                    "error which will clear itself." % {'array': u4v_vmax_id})

            helper.log_info("Array: %(array)s - Initiator level metrics "
                            "collected." % {'array': u4v_vmax_id})

        # Get WLP info
        if select_wlp:
            for comp in rf.get_wlp_compliance_details():
                try:
                    comp_event = helper.new_event(source=u4v_source,
                                                  index=spl_index,
                                                  sourcetype=spl_sourcetype,
                                                  data=comp)
                    ew.write_event(comp_event)
                except TypeError:
                    helper.log_error(
                        "Array: %(array)s WLP Compliance: %(comp)s - There "
                        "was an issue collecting Compliance metrics, please "
                        "check status code for further information. This may "
                        "be a temporary Unisphere response error which will "
                        "clear itself." % {
                            'array': u4v_vmax_id,
                            'comp': comp})

            helper.log_info("Array: %(array)s - Compliance level metrics "
                            "collected" % {'array': u4v_vmax_id})

            for head in rf.get_wlp_headroom_details():
                try:
                    head_event = helper.new_event(source=u4v_source,
                                                  index=spl_index,
                                                  sourcetype=spl_sourcetype,
                                                  data=head)
                    ew.write_event(head_event)
                except TypeError:
                    helper.log_error(
                        "Array: %(array)s WLP Headroom: %(head)s - There was "
                        "an issue collecting Headroom metrics, please check "
                        "status code for further information. This may be a "
                        "temporary Unisphere response error which will clear "
                        "itself." % {
                            'array': u4v_vmax_id,
                            'head': head})

            helper.log_info("Array: %(array)s - Headroom level metrics "
                            "collected" % {'array': u4v_vmax_id})

        rf.close_session()

        helper.log_info(
            "Array: %(array)s - Finished metrics collection run" % {
                'array': u4v_vmax_id})
