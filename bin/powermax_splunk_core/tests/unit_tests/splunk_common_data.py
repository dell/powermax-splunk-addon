"""bin/powermax_splunk_core/tests/unit_tests/splunk_common_data.py"""

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


class CommonData(object):
    """Common data."""
    # Version info
    U4P_VERSION = '100'
    SERVER_VERSION = {'version': 'V10.0.0.0'}

    # Splunk Input Configuration
    U4P_IP_ADDRESS = '8.8.8.8'
    U4P_PORT = '8443'
    U4P_USERNAME = 'splunk_user'
    U4P_PASSWORD = 'splunk_password'
    U4P_POWERMAX_ID_A = '000123456789'
    U4P_POWERMAX_ID_B = '000987654321'

    U4P_REST_TIMEOUT = 60
    U4P_ENABLE_SSL = True
    U4P_SSL_CERT_LOC = '/path/to/cert.pem'

    SPLUNK_INTERVAL = 300
    SPLUNK_SOURCE = 'JSON'
    SPLUNK_INDEX = 'main'

    SELECT_ARRAY = 'array_all'
    SELECT_SRP = 'srp_all'
    SELECT_SG = 'sg_all'
    SELECT_DIR = 'dir_all'
    SELECT_PORT = 'port_all'
    SELECT_PG = 'pg_all'
    SELECT_HOST = 'host_all'
    SELECT_INIT = 'init_all'
    SELECT_MV = 'mv_all'
    SELECT_ISCSI = 'iscsi_all'
    SELECT_RDF = 'rdf_all'
    SELECT_METRO_DR = 'metro_on'
    SELECT_SNAP_POLICY = 'sp_on'
    SELECT_ALERTS = 'audit_on'
    SELECT_AUDIT = 'alerts_on'

    SELECT_ARRAY_METRICS = 'BEReqs, BEIOs, HostIOs, fake_metric'
    SELECT_SRP_METRICS = 'HostIOs, HostMBReads'
    SELECT_SG_METRICS = 'fake_metric'
    SELECT_FE_DIR_METRICS = 'HostIOs, HostMBs'
    SELECT_BE_DIR_METRICS = 'IOs, MBRead'
    SELECT_RDF_DIR_METRICS = 'CopyIOs, CopyMBs'
    SELECT_IM_DIR_METRICS = 'PercentBusy'
    SELECT_EDS_DIR_METRICS = 'RandomWriteMissMBs, RandomWriteMisses'
    SELECT_FE_PORT_METRICS = 'IOs, MBRead'
    SELECT_BE_PORT_METRICS = 'Reads, Writes'
    SELECT_RDF_PORT_METRICS = 'Reads, SpeedGBs'
    SELECT_PG_METRICS = 'MBs, PercentBusy'
    SELECT_HOST_METRICS = 'HostMBWrites, MBs'
    SELECT_INIT_METRICS = 'ReadResponseTime, Reads'
    SELECT_MV_METRICS = 'ResponseTime, WriteResponseTime'
    SELECT_ISCSI_TGT_METRICS = 'PacketCount, Reads'
    SELECT_IP_INTERFACE_METRICS = 'Reads, ResponseTime'
    SELECT_RDFS_METRICS = 'BEMBReads, BEMBTransferred'
    SELECT_RDFA_METRICS = 'AvgCycleSize, AvgCycleTime'

    HELPER_ARG_MAP_LIST = [
        'select_array', 'select_srp', 'select_sg', 'select_director',
        'select_port', 'select_pg', 'select_iscsi', 'select_host',
        'select_mv', 'select_initiator', 'select_rdf', 'select_metro_dr',
        'select_snap_policy', 'select_alerts', 'select_audit_logs']

    # Time
    ONE_MINUTE = 60000
    ONE_HOUR = 3600000
    TIMESTAMP = int(time.time()) * 1000

    # Asset Dummy IDs
    srp_id_a = 'SRP_1'
    srp_id_b = 'SRP_2'

    storage_group_a = 'test_sg_a'
    storage_group_b = 'test_sg_b'

    service_level_diamond = 'Diamond'
    service_level_none = 'None'

    port_group_a = 'test_pg_a'
    port_group_b = 'test_pg_b'

    masking_view_a = 'test_mv_a'
    masking_view_b = 'test_mv_b'

    host_a = 'test_host_a'
    host_b = 'test_host_b'
    host_group_a = 'test_host_group_a'
    host_group_b = 'test_host_group_b'

    initiator_a = '10000000c9a6b7d1'
    initiator_b = '10000000c9a6b7d2'

    fe_director = 'FA-1D'
    iscsi_director = 'SE-1D'
    be_director = 'DF-1D'
    rdf_director = 'RF-1D'
    im_director = 'IM-1D'
    eds_director = 'ED-1D'

    dir_port_a = '{}:{}'.format(fe_director, '1')
    dir_port_b = '{}:{}'.format(fe_director, '1')

    dir_port_init_a = '{}:{}:{}'.format(fe_director, '1', initiator_a)
    dir_port_init_b = '{}:{}:{}'.format(fe_director, '1', initiator_b)

    fe_port_key = {'directorId': fe_director, 'portId': '1'}
    iscsi_port_key = {'directorId': iscsi_director, 'portId': '1'}
    be_port_key = {'directorId': be_director, 'portId': '1'}
    rdf_port_key = {'directorId': rdf_director, 'portId': '1'}

    rdfg_num_a = 1
    rdfg_label_a = 'rdfg_a'
    rdfg_num_b = 2
    rdfg_label_b = 'rdfg_b'

    rdf_director_srdf_groups = {'srdf_groups': [
        {'rdf_group_number': rdfg_num_a, 'label': rdfg_label_a},
        {'rdf_group_number': rdfg_num_b, 'label': rdfg_label_b}]}

    volume_a = '0000A'
    volume_b = '0000B'
    host_lun_address_a = '0001'
    host_lun_address_b = '0002'

    ip_address_a = '10.10.10.10'
    ip_address_b = '10.10.10.11'
    ip_address_network_a = '10.10.10.10-1'
    ip_address_network_b = '10.10.10.11-2'

    iscsi_target_iqn_a = 'iqn.1992-04.com.emc:600009700'
    iscsi_target_iqn_b = 'iqn.1992-04.com.emc:600009701'

    # ============== #
    # Call responses #
    # ============== #

    # >>> Performance Helper Methods
    # List categories
    get_diagnostic_categories = {
        'categoryName': [
            'Array', 'BEDirector', 'BEPort', 'BeEmulation', 'Board',
            'CachePartition', 'DeviceGroup', 'DiskGroup', 'EDSDirector',
            'EDSEmulation', 'EMDirector', 'ExternalDirector', 'ExternalDisk',
            'ExternalDiskGroup', 'FEDirector', 'FEPort', 'FiconEmulation',
            'FeEmulation', 'FiconEmulationThread', 'FiconPortThread', 'Host',
            'IMDirector', 'IMEmulation', 'IPInterface', 'ISCSITarget',
            'Initiator', 'MaskingView', 'PortGroup', 'RDFA', 'RDFDirector',
            'RDFEmulation', 'RDFPort', 'RDFS', 'SDNASFileSystem',
            'SDNASInterface', 'SDNASNode', 'SDNASServer', 'SRP',
            'StorageContainer', 'StorageGroup', 'StorageResource', 'ThinPool',
            'cloudprovider', 'zHyperLinkPort']}
    # List metrics
    get_metrics_list = {
        'metricName': [
            'BEIOs', 'BEReadReqs', 'FEReadReqs', 'HostMBs', 'HostIOs']}

    # >>> SLO Provisioning level calls
    # Array
    get_array_list = {'symmetrixId': [U4P_POWERMAX_ID_A, U4P_POWERMAX_ID_B]}
    get_array_slo_pro_details = {
        'symmetrixId': U4P_POWERMAX_ID_A, 'local': True, 'device_count': 616,
        'physicalCapacity': {
            'used_capacity_gb': 1000.00, 'total_capacity_gb': 1000.00}}

    # SRP
    get_srp_list = {'srpId': [srp_id_a, srp_id_b]}
    get_srp_details = {
        'service_levels': [service_level_diamond, service_level_none],
        'num_of_disk_groups': 1,
        'srpId': srp_id_a,
        'srp_capacity': {'usable_total_tb': 24.45},
        'reserved_cap_percent': 10,
        'diskGroupId': ['1'],
        'srp_efficiency': {'overall_efficiency_ratio_to_one': 3179.4}}

    # Storage Group
    get_sg_list = {'storageGroupId': [storage_group_a, storage_group_b]}
    get_storage_group_details = {
        'srp': srp_id_a, 'service_level': service_level_diamond,
        'storageGroupId': storage_group_a, 'slo_compliance': 'STABLE'}

    # Port Group
    get_pg_list = {'portGroupId': [port_group_a, port_group_b]}
    get_pg_details = {
        'portGroupId': port_group_a, 'num_of_masking_views': 1,
        'type': 'Fibre', 'num_of_ports': 1,
        'symmetrixPortKey': [fe_port_key],
        'maskingview': [masking_view_a]}

    # Host
    get_host_list = {'hostId': [host_a, host_b]}
    get_host_details = {
        'hostId': host_a, 'type': 'Fibre', 'num_of_initiators': 2,
        'enabled_flags': 'test_flag_a, test_flag_b', 'disabled_flags': '',
        'initiator': [initiator_a, initiator_b],
        'maskingview': [masking_view_a],
        'powerpathhosts': [host_a]}

    # Initiator
    get_initiator_list = {'initiatorId': [dir_port_init_a, dir_port_init_b]}
    get_initiator_details = {
        'initiatorId': initiator_a, 'logged_in': True, 'type': 'Fibre',
        'flags_in_effect': 'test_flag_a, test_flag_b',
        'enabled_flags': [], 'disabled_flags': [],
        'symmetrixPortKey': [{'directorId': fe_director, 'portId': '1'}]}

    # Masking View
    get_masking_view_list = {'maskingViewId': [masking_view_a, masking_view_b]}
    get_masking_view_details = {
        'maskingViewId': masking_view_a, 'portGroupId': port_group_a,
        'storageGroupId': storage_group_a, 'hostId': host_a}
    get_masking_view_connections = {
        'maskingViewConnection': [
            {'volumeId': volume_a, 'dir_port': dir_port_a,
             'initiatorId': initiator_a,
             'host_lun_address': host_lun_address_a},
            {'volumeId': volume_b, 'dir_port': dir_port_b,
             'initiatorId': initiator_b,
             'host_lun_address': host_lun_address_b}]}

    # >>> System level calls
    get_system_array_list = {'symmetrixId': [U4P_POWERMAX_ID_A,
                                             U4P_POWERMAX_ID_B]}
    get_system_array_info = {
        'symmetrixId': U4P_POWERMAX_ID_A, 'all_flash': True, 'disk_count': 16,
        'system_sized_property': [{
            'srp_name': 'SRP_1', 'sized_fba_capacity_tb': 69}]}

    get_system_array_health = {
        'num_failed_disks': 0,
        'health_check': [TIMESTAMP],
        'health_score_metric': [
            {'metric': 'SERVICE_LEVEL_COMPLIANCE',
             'instance_metrics': [{'health_score_instance_metric': []}],
             'health_score': 100.0},
            {'metric': 'OVERALL',
             'instance_metrics': [{'health_score_instance_metric': []}],
             'health_score': 100.0}]}

    get_system_array_alerts = {
        'serverAlertSummary': {'alert_count': 5},
        'symmAlertSummary': [
            {'performanceAlertSummary': {'alert_count': 4},
             'symmId': U4P_POWERMAX_ID_A,
             'arrayAlertSummary': {'alert_count': 6}},
            {'performanceAlertSummary': {'alert_count': 1},
             'symmId': U4P_POWERMAX_ID_B,
             'arrayAlertSummary': {'alert_count': 3}}]}

    get_system_director_list = {'directorId': [
        fe_director, iscsi_director, be_director, rdf_director, im_director,
        eds_director]}
    get_system_director_details = {
        'directorId': fe_director, 'availability': 'Online',
        'director_number': 49, 'num_of_cores': 6, 'director_slot_number': 1,
        'num_of_ports': 8}

    get_system_port_list = {
        'symmetrixPortKey': [fe_port_key, be_port_key, rdf_port_key]}
    get_system_iscsi_port_list = {'symmetrixPortKey': [iscsi_port_key]}
    get_system_port_details = {
        'symmetrixPort': {
            'director_status': 'Online', 'port_status': 'ON',
            'num_of_cores': 6, 'num_of_port_groups': '1',
            'maskingview': [masking_view_a],
            'symmetrixPortKey': {'directorId': fe_director, 'portId': '1'},
            'portgroup': [port_group_a]}}
    get_system_iscsi_port_details = {
        'symmetrixPort': {
            'director_status': 'Online', 'port_status': 'ON',
            'num_of_cores': 6, 'num_of_port_groups': '1',
            'maskingview': [masking_view_a],
            'symmetrixPortKey': {'directorId': iscsi_director, 'portId': '1'},
            'portgroup': [port_group_a], 'identifier': iscsi_target_iqn_a}}

    get_system_ip_interface_list = {'ipInterfaceId': [
        ip_address_network_a, ip_address_network_b]}
    get_system_ip_interface = {
        'ip_interface_id': ip_address_network_a, 'network_id': 2,
        'ip_prefix_length': 2, 'vlan_id': 1, 'mtu': 1500,
        'iscsi_target_director': iscsi_director,
        'iscsi_target_port': 0, 'ip_address': ip_address_a}

    # System Alerts
    get_system_alert_list = {'alertId': [
        '07172bfe-2885-45ea-9722-392660a16d04',
        '0a93506a-8dec-4254-847d-251e396af434']}

    get_system_alert_details = {
        'array': U4P_POWERMAX_ID_A, 'object': 'splunk-obj',
        'alertId': '07172bfe-2885-45ea-9722-392660a16d04'}

    # Audit Logs
    get_audit_log_list = {'maxPageSize': 1000, 'count': 2, 'resultList': {
        'result': [{'record_id': 10000}, {'record_id': 10001}]}}

    get_audit_log = {'objectList': [{
        'message': 'Processing started  ', 'entry_date': int(time.time()),
        'record_id': 298011, 'username': 'X:SPLUNK-1\\test_user'}]}

    # >>> WLP level calls
    get_array_wlp_capabilities = {
        'symmetrixCapability': [
            {'symmetrixId': U4P_POWERMAX_ID_A, 'workloadDetailCapable': True},
            {'symmetrixId': U4P_POWERMAX_ID_B, 'workloadDetailCapable': False}
        ]}

    # >>> Migration level calls
    get_array_migration_info = {
        'storageGroupCount': 5, 'arrayId': U4P_POWERMAX_ID_A,
        'local': True, 'migrationSessionCount': 0}

    get_array_migration_capabilities = {
        'storageArrayCapability': [
            {'dmSource': True, 'dmTarget': True, 'arrayId': U4P_POWERMAX_ID_A},
            {'dmSource': True, 'dmTarget': False, 'arrayId': U4P_POWERMAX_ID_B}
        ]}

    # >>> Replication level calls
    # Get Array Replication capabilities
    get_array_replication_capabilities = {
        'symmetrixCapability': [
            {'symmetrixId': U4P_POWERMAX_ID_A, 'rdfCapable': True},
            {'symmetrixId': U4P_POWERMAX_ID_B, 'rdfCapable': False}]}

    # RDF Group
    get_rdf_group_list = {'rdfGroupID': [
        {'rdfgNumber': 1, 'label': 'label_1'},
        {'rdfgNumber': 2, 'label': 'label_2'},
        {'rdfgNumber': 3, 'label': 'label_3'},
        {'rdfgNumber': 4, 'label': 'label_4'}]}

    get_rdf_group_details = {
        'rdfgNumber': 1, 'label': 'label_1', 'type': 'Dynamic',
        'remoteSymmetrix': U4P_POWERMAX_ID_B, 'remoteRdfgNumber': 1,
        'localPorts': ['RF-1D:1', 'RF-1D:2'],
        'remotePorts': ['RF-1D:1', 'RF-1D:2']}

    # RDF Group Volume
    get_rdf_group_volume_list = {'name': [volume_a, volume_b]}

    get_rdf_group_volume = {
        'localVolumeName': volume_a, 'remoteVolumeName': volume_b}

    # Metro DR
    get_metro_dr_list = {'names': ['env_a', 'env_b']}

    get_metro_dr_details = {
        'environment_state': 'Invalid, Manual Recovery',
        'name': 'env_a', 'dr_rdf_mode': 'Adaptive Copy'}

    # Snapshot Policies
    get_snapshot_policy_list = {'name': ['SmallCounts', 'DailyDefault']}

    get_snapshot_policy_details = {
        'symmetrixID': U4P_POWERMAX_ID_A, 'provider_name': 'test_provider',
        'snapshot_policy_name': 'DailyDefault'}

    # >>> Performance level calls
    # Dummy performance response for all categories
    dummy_performance_response = {'resultList': {
        'from': 1, 'to': 2, 'result': [
            {'PercentBusy': 0.027849833, 'timestamp': TIMESTAMP}]},
        'count': 2, 'expirationTime': TIMESTAMP, 'maxPageSize': 1000,
        'id': 'c2c3a5bd-5bed-41b2-be7c-24376496bc73_0'}

    # Array
    get_array_registration = {'isRegistered': True}
    get_array_keys = {'arrayInfo': [
        {'symmetrixId': U4P_POWERMAX_ID_A, 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP},
        {'symmetrixId': U4P_POWERMAX_ID_B, 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP}]}

    # Host
    get_host_keys = {'hostInfo': [
        {'hostId': host_a, 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP},
        {'hostId': host_b, 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP}]}

    # Initiator
    get_initiator_keys = {'initiatorInfo': [
        {'initiatorId': initiator_a, 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP},
        {'initiatorId': initiator_b, 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP}]}

    # iSCSI Target
    get_iscsi_target_keys = {'iSCSITargetInfo': [
        {'iscsiTargetId': iscsi_target_iqn_a, 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP},
        {'iscsiTargetId': iscsi_target_iqn_b, 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP}]}

    # RDFA Group
    get_rdfa_keys = {'rdfaInfo': [
        {'raGroupId': '1', 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP},
        {'raGroupId': '2', 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP}]}

    # RDFS Group
    get_rdfs_keys = {'rdfsInfo': [
        {'raGroupId': '3', 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP},
        {'raGroupId': '4', 'firstAvailableDate': TIMESTAMP,
         'lastAvailableDate': TIMESTAMP}]}
