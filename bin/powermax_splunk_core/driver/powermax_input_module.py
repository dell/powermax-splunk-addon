"""bin/powermax_splunk_core/driver/powermax_input_module.py"""
# encoding = utf-8

# Copyright (c) 2021 Dell Inc. or its subsidiaries.
#
# Licensed under the Splunk End User License Agreement for Third-Party Content
# (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at
#
#        https://github.com/dell/powermax-splunk-addon/blob/main/LICENSE
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import time

import PyU4V.utils.exception

# Try/Except needed for variation in production/test environments
try:
    import ta_dellemc_vmax_declare
except (ImportError, ValueError):
    from ... import ta_dellemc_vmax_declare # NOQA

from .powermax_splunk import PMaxSplunk

PYU4V_EXCEPTIONS = (PyU4V.utils.exception.ResourceNotFoundException,
                    PyU4V.utils.exception.VolumeBackendAPIException,
                    PyU4V.utils.exception.InvalidInputException)


def validate_input(*args, **kwargs):
    """Validation of input and environment is handled in PMaxSplunk.

    Note: Thorough validations tests are run when data input is instantiated
    in PMaxSplunk().
    """


def collect_events(helper, ew):
    """Implement your data collection logic here"""
    # Initialise connection to Unisphere
    start_time = time.time()
    pmax = PMaxSplunk(helper=helper, event_writer=ew)
    pmax.log_info('Starting metrics collection run.')

    # Collect Array level metrics
    if pmax.enabled_categories.get('array'):
        try:
            array_details = pmax.get_array_details()
            pmax.write_event(data=array_details)
        except PYU4V_EXCEPTIONS:
            pmax.log_collection_error(asset_type='Array')
        pmax.log_info('Array collection complete.')

    # Collect SRP level metrics
    if pmax.enabled_categories.get('srp'):
        for srp in pmax.conn.provisioning.get_srp_list():
            try:
                srp_details = pmax.get_srp_details(srp_id=srp)
                pmax.write_event(data=srp_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(asset_type='SRP', asset_id=srp)
        pmax.log_info('SRP collection complete.')

    # Collect SG level metrics
    if pmax.enabled_categories.get('storage_group'):
        for sg in pmax.conn.provisioning.get_storage_group_list():
            try:
                sg_details = pmax.get_storage_group_details(
                    storage_group_id=sg)
                pmax.write_event(data=sg_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Storage Group', asset_id=sg)
        pmax.log_info('Storage Group collection complete.')

    # Collect Director level metrics
    if pmax.enabled_categories.get('director'):
        for director in pmax.conn.provisioning.get_director_list():
            try:
                dir_details = pmax.get_director_details(director_id=director)
                pmax.write_event(data=dir_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Director', asset_id=director)
        pmax.log_info('Director collection complete.')

    # Get Port level metrics
    if pmax.enabled_categories.get('port'):
        for port in pmax.conn.provisioning.get_port_list():
            try:
                port_details = pmax.get_port_details(port_key=port)
                pmax.write_event(data=port_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Port', asset_id=port)
        pmax.log_info('Port collection complete.')

    # Get Port Group level metrics
    if pmax.enabled_categories.get('port_group'):
        for port_group in pmax.conn.provisioning.get_port_group_list():
            try:
                pg_details = pmax.get_port_group_details(
                    port_group_id=port_group)
                pmax.write_event(data=pg_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Port Group', asset_id=port_group)
        pmax.log_info('Port Group collection complete.')

    # Get Host level metrics
    if pmax.enabled_categories.get('host'):
        active_hosts = pmax.get_active_host_set()
        for host in pmax.conn.provisioning.get_host_list():
            try:
                host_details = pmax.get_host_details(
                    host_id=host, active_host_set=active_hosts)
                pmax.write_event(data=host_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Host', asset_id=host)
        pmax.log_info('Host collection complete.')

    # Get Initiator level metrics
    if pmax.enabled_categories.get('initiator'):
        active_inits = pmax.get_active_initiator_set()
        for init in pmax.conn.provisioning.get_initiator_list():
            try:
                init_details = pmax.get_initiator_details(
                    initiator_id=init, active_initiator_set=active_inits)
                pmax.write_event(data=init_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Initiator', asset_id=init)
        pmax.log_info('Initiator collection complete.')

    # Get Masking View metrics
    if pmax.enabled_categories.get('masking_view'):
        for mv in pmax.conn.provisioning.get_masking_view_list():
            try:
                mv_details = pmax.get_masking_view_details(
                    masking_view_id=mv)
                pmax.write_event(data=mv_details)
                for conn in pmax.get_masking_view_connections(
                        masking_view_id=mv):
                    pmax.write_event(data=conn)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Masking View', asset_id=mv)
        pmax.log_info('Masking View collection complete.')

    # Get iSCSI related metrics
    if pmax.enabled_categories.get('iscsi'):
        # Get IP interface metrics
        ip_int_list = pmax.get_ip_interface_list()
        for ip_int in ip_int_list:
            for ip in ip_int.get('ip_interface_list'):
                try:
                    int_data = pmax.get_ip_interface_details(
                        director_id=ip_int.get('director_id'),
                        port_id=ip_int.get('port_id'),
                        interface_id=ip)
                    pmax.write_event(data=int_data)
                except PYU4V_EXCEPTIONS:
                    pmax.log_collection_error(
                        asset_type='IP Interface', asset_id=ip)
        pmax.log_info('IP Interface collection complete.')
        # Get iSCSI Target data
        iscsi_tgt_port_list = pmax.get_iscsi_target_list()
        for iscsi_tgt in iscsi_tgt_port_list:
            try:
                iscsi_tgt_details = pmax.get_iscsi_target_details(
                    iscsi_tgt)
                pmax.write_event(data=iscsi_tgt_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='iSCSI Target', asset_id='{d}:{p}'.format(
                        d=iscsi_tgt.get('director_id'),
                        p=iscsi_tgt.get('port_id')))
        pmax.log_info('iSCSI Target collection complete.')

    # Get RDFG related metrics
    if pmax.enabled_categories.get('rdf'):
        rdfg_map = pmax.get_rdf_group_map()
        for rdfg_num in rdfg_map.keys():
            try:
                rdfg_data = pmax.get_rdf_group_details(rdfg_num, rdfg_map)
                pmax.write_event(data=rdfg_data)
                rdfg_pair_list = (
                    pmax.conn.replication.get_rdf_group_volume_list(
                        rdf_number=rdfg_num))
                for vol in rdfg_pair_list:
                    try:
                        vol_data = pmax.get_rdf_pair_details(rdfg_data, vol)
                        pmax.write_event(data=vol_data)
                    except PYU4V_EXCEPTIONS:
                        pmax.log_collection_error(
                            asset_type='RDF Pair', asset_id=vol)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='RDF Group', asset_id=rdfg_num)
        pmax.log_info('RDF Group collection complete.')

    # Get Metro DR metrics
    if pmax.enabled_categories.get('metro_dr'):
        mdr_env_list = pmax.conn.metro_dr.get_metrodr_environment_list()
        for mdr_env in mdr_env_list:
            try:
                mdr_env_data = pmax.get_metro_dr_environment_details(mdr_env)
                pmax.write_event(data=mdr_env_data)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Metro DR', asset_id=mdr_env)
        pmax.log_info('Metro DR collection complete.')

    # Get Snapshot Policy metrics
    if pmax.enabled_categories.get('snap_policy'):
        snap_policy_list = pmax.conn.snapshot_policy.get_snapshot_policy_list()
        for sp in snap_policy_list:
            try:
                sp_data = pmax.get_snapshot_policy_details(sp)
                pmax.write_event(data=sp_data)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Snapshot Policy', asset_id=sp)
        pmax.log_info('Snapshot Policy collection complete.')

    # Collect Alerts
    if pmax.enabled_categories.get('alerts'):
        for alert in pmax.get_alert_list():
            try:
                alert_details = pmax.get_alert(alert_id=alert)
                pmax.write_event(data=alert_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(asset_type='Alert', asset_id=alert)
        pmax.log_info('Alerts collection complete.')

    # Get Audit Logs
    if pmax.enabled_categories.get('audit_logs'):
        audit_list = pmax.get_audit_log_record_list()
        for audit in audit_list:
            try:
                audit_details = pmax.get_audit_log_record_details(
                    record_id=audit)
                pmax.write_event(data=audit_details)
            except PYU4V_EXCEPTIONS:
                pmax.log_collection_error(
                    asset_type='Audit Log', asset_id=audit)
        pmax.log_info('Audit Log collection complete.')

    end_time = time.time()

    # Close the session and finish array collection run
    pmax.conn.close_session()
    pmax.log_info('Finished collection run.')
    pmax.process_collection_duration(start_time=start_time, end_time=end_time)
