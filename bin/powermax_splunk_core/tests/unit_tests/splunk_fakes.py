"""bin/powermax_splunk_core/tests/unit_tests/splunk_fakes.py"""

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

import json

from copy import deepcopy
from unittest import mock

from . import splunk_common_data

scd = splunk_common_data.CommonData()


class FakeResponse(object):
    """Fake response."""

    def __init__(self, status_code, return_object, raw_reason=None, text=None,
                 content=None):
        """Fake REST response.

        :param status_code: response status code -- int
        :param return_object: REST response object -- dict
        :param raw_reason: REST raw reason -- dict
        :param text: JSON formatted test -- dict
        :param content: REST response content -- dict
        """
        self.status_code = status_code
        self.return_object = return_object
        self.raw = mock.MagicMock()
        self.raw.reason = raw_reason
        self.text = json.dumps(text, sort_keys=True, indent=4)
        self.content = content

    def json(self):
        """response.json response functionality.

        :returns: REST return object -- dict
        """
        if self.return_object:
            return self.return_object


class FakeRequestsSession(object):
    """Fake request session."""

    def __init__(self):
        """__init__."""

    def request(self, method, url, params=None, data=None, timeout=None): # NOQA
        """Fake REST request response object handler.

        :param method: REST method, GET, POST etc. -- str
        :param url: the target REST URL -- str
        :param params: REST query parameters -- dict
        :param data: REST request object -- dict
        :param timeout: REST timeout value -- int
        :returns: fake REST response -- obj
        """
        return_object = ''
        status_code = 200
        raw_reason = None
        text = None

        url_components = list(filter(None, url.split('/')))
        uri = url_components[url_components.index('restapi') + 1:]
        try:
            uri.remove(scd.U4P_VERSION)
        except ValueError:
            pass
        rest_category = uri[0]

        if rest_category == 'version':
            return_object = scd.SERVER_VERSION

        elif rest_category == 'performance':
            status_code, return_object = self._performance_call(uri)

        elif rest_category == 'sloprovisioning':
            status_code, return_object = self._sloprovisioning_call(
                uri, params)

        elif rest_category == 'system':
            status_code, return_object = self._system_call(uri)

        elif rest_category == 'wlp':
            status_code, return_object = self._wlp_call(uri)

        elif rest_category == 'migration':
            status_code, return_object = self._migration_call(uri)

        elif rest_category == 'replication':
            status_code, return_object = self._replication_call(uri)

        return FakeResponse(status_code, return_object, raw_reason, text)

    @staticmethod
    def _replication_call(uri):
        """Calls to /replication endpoints.

        :param uri: uniform resource identifier -- list
        :returns: status code, response -- int, dict/None
        """
        status_code = 200
        return_object = None

        # Get Array replication capabilities
        if 'capabilities' == uri[-2] and 'symmetrix' == uri[-1]:
            return_object = deepcopy(scd.get_array_replication_capabilities)

        # RDF Group
        elif 'rdf_group' == uri[-1]:
            return_object = deepcopy(scd.get_rdf_group_list)
        elif 'rdf_group' == uri[-2]:
            return_object = deepcopy(scd.get_rdf_group_details)
            return_object['rdfgNumber'] = int(uri[-1])

        # RDF Group Volume
        elif 'rdf_group' == uri[-3] and 'volume' == uri[-1]:
            return_object = deepcopy(scd.get_rdf_group_volume_list)
        elif 'rdf_group' == uri[-4] and 'volume' == uri[-2]:
            return_object = deepcopy(scd.get_rdf_group_volume)
            return_object['localRdfGroupNumber'] = int(uri[-3])
            return_object['localVolumeName'] = uri[-1]

        # Metro DR
        elif 'metrodr' == uri[-1]:
            return_object = deepcopy(scd.get_metro_dr_list)
        elif 'metrodr' == uri[-2]:
            return_object = deepcopy(scd.get_metro_dr_details)
            return_object['name'] = uri[-1]

        # Snapshot Policies
        elif 'snapshot_policy' == uri[-1]:
            return_object = deepcopy(scd.get_snapshot_policy_list)
        elif 'snapshot_policy' == uri[-2]:
            return_object = deepcopy(scd.get_snapshot_policy_details)
            return_object['name'] = uri[-1]

        return status_code, return_object

    @staticmethod
    def _wlp_call(uri):
        """Calls to /wlp endpoints.

        :param uri: uniform resource identifier -- list
        :returns: status code, response -- int, dict/None
        """
        status_code = 200
        return_object = None

        if 'capabilities' == uri[-2] and 'symmetrix' == uri[-1]:
            return_object = deepcopy(scd.get_array_wlp_capabilities)

        return status_code, return_object

    @staticmethod
    def _migration_call(uri):
        """Calls to /migration endpoints.

        :param uri: uniform resource identifier -- list
        :returns: status code, response -- int, dict/None
        """
        status_code = 200
        return_object = None

        if 'symmetrix' == uri[-2]:
            return_object = deepcopy(scd.get_array_migration_info)
            return_object['arrayId'] = uri[-1]

        elif 'capabilities' == uri[-2] and 'symmetrix' == uri[-1]:
            return_object = deepcopy(scd.get_array_migration_capabilities)

        return status_code, return_object

    @staticmethod
    def _sloprovisioning_call(uri, params):
        """Calls to /sloprovisioning endpoints.

        :param uri: uniform resource identifier -- list
        :param params: request parameters -- dict
        :returns: status code, response -- int, dict/None
        """
        status_code = 200
        return_object = None

        # Array level calls
        if 'symmetrix' == uri[-1]:
            return_object = deepcopy(scd.get_array_list)
        elif 'symmetrix' == uri[-2]:
            return_object = deepcopy(scd.get_array_slo_pro_details)
            return_object['symmetrixId'] = uri[-1]

        # SRP level calls
        elif 'srp' == uri[-1]:
            return_object = deepcopy(scd.get_srp_list)
        elif 'srp' == uri[-2]:
            return_object = deepcopy(scd.get_srp_details)
            return_object['srpId'] = uri[-1]

        # SG level calls
        elif 'storagegroup' == uri[-1]:
            return_object = deepcopy(scd.get_sg_list)
        elif 'storagegroup' == uri[-2]:
            return_object = deepcopy(scd.get_storage_group_details)
            return_object['storageGroupId'] = uri[-1]

        # Port level calls
        elif 'port' == uri[-1]:
            if params and params.get('iscsi_target'):
                return_object = deepcopy(scd.get_system_iscsi_port_list)
            else:
                return_object = deepcopy(scd.get_system_port_list)

        # Port Group level calls
        elif 'portgroup' == uri[-1]:
            return_object = deepcopy(scd.get_pg_list)
        elif 'portgroup' == uri[-2]:
            return_object = deepcopy(scd.get_pg_details)
            return_object['portGroupId'] = uri[-1]

        # Host level calls
        elif 'host' == uri[-1]:
            return_object = deepcopy(scd.get_host_list)
        elif 'host' == uri[-2]:
            return_object = deepcopy(scd.get_host_details)
            return_object['hostId'] = uri[-1]

        # Initiator level calls
        elif 'initiator' == uri[-1]:
            return_object = deepcopy(scd.get_initiator_list)
        elif 'initiator' == uri[-2]:
            return_object = deepcopy(scd.get_initiator_details)
            return_object['initiatorId'] = uri[-1].split(':')[2]

        # Masking View level calls
        elif 'maskingview' == uri[-1]:
            return_object = deepcopy(scd.get_masking_view_list)
        elif 'maskingview' == uri[-2]:
            return_object = deepcopy(scd.get_masking_view_details)
            return_object['maskingViewId'] = uri[-1]
        elif 'maskingview' == uri[-3] and 'connections' == uri[-1]:
            return_object = deepcopy(scd.get_masking_view_connections)

        return status_code, return_object

    @staticmethod
    def _system_call(uri):
        """Calls to /system endpoints.

        :param uri: uniform resource identifier -- list
        :returns: status code, response -- int, dict/None
        """
        status_code = 200
        return_object = None

        # Get rid of uri params used for audit logs
        if '?' in uri[-1]:
            uri[-1] = uri[-1].split('?')[0]

        # Get array details
        if 'symmetrix' == uri[-2]:
            return_object = deepcopy(scd.get_system_array_info)
            return_object['symmetrixId'] = uri[-1]

        # Get director details
        elif 'director' == uri[-1]:
            return_object = deepcopy(scd.get_system_director_list)
        elif 'director' == uri[-2]:
            return_object = deepcopy(scd.get_system_director_details)
            return_object['directorId'] = uri[-1]
            if any(x in uri[-1] for x in ['RF', 'RE']):
                return_object.update(scd.rdf_director_srdf_groups)

        # Get port details
        elif 'port' == uri[-1]:
            return_object = deepcopy(scd.get_system_port_list)
        elif 'port' == uri[-2]:
            if 'SE' in uri[-3]:
                return_object = deepcopy(scd.get_system_iscsi_port_details)
            else:
                return_object = deepcopy(scd.get_system_port_details)
            return_object[
                'symmetrixPort']['symmetrixPortKey']['directorId'] = uri[-3]
            return_object[
                'symmetrixPort']['symmetrixPortKey']['portId'] = uri[-1]

        # Get IP Interface list
        elif 'ipinterface' == uri[-1]:
            return_object = deepcopy(scd.get_system_ip_interface_list)
        elif 'ipinterface' == uri[-2]:
            return_object = deepcopy(scd.get_system_ip_interface)
            return_object['ip_interface_id'] = uri[-1]
            return_object['iscsi_target_port'] = uri[-3]
            return_object['iscsi_target_director'] = uri[-5]
            ip_net = uri[-1].split('-')
            return_object['ip_address'] = ip_net[0]
            return_object['network_id'] = ip_net[1]

        # Get array alert summary details
        elif 'alert_summary' == uri[-1]:
            return_object = deepcopy(scd.get_system_array_alerts)

        # Get array alert details
        elif 'alert' == uri[-1]:
            return_object = deepcopy(scd.get_system_alert_list)
        elif 'alert' == uri[-2]:
            return_object = deepcopy(scd.get_system_array_health)
            return_object['alertId'] = uri[-1]

        # Get audit log details
        elif 'audit_log_record' == uri[-1]:
            return_object = deepcopy(scd.get_audit_log_list)
        elif 'audit_log_record' == uri[-2]:
            return_object = deepcopy(scd.get_audit_log)
            return_object['record_id'] = int(uri[-1])

        # Get array health details
        elif 'health' == uri[-1]:
            return_object = deepcopy(scd.get_system_array_health)

        return status_code, return_object

    @staticmethod
    def _performance_call(uri):
        """Calls to /performance endpoints.

        :param uri: uniform resource identifier -- list
        :returns: status code, response -- int, dict/None
        """
        return_object = list()
        status_code = 200
        perf_idx = uri.index('performance')
        performance_section = uri[perf_idx + 1]
        category = uri[perf_idx + 2]

        # Get performance data
        if category == 'metrics':
            return_object = deepcopy(scd.dummy_performance_response)
        elif category == 'help':
            if uri[-1] == 'categories':
                return_object = deepcopy(scd.get_diagnostic_categories)
            if uri[-2] == 'metrics':
                return_object = deepcopy(scd.get_metrics_list)

        # Get category level specific information
        elif performance_section == 'Array':
            if category == 'registration':
                return_object = deepcopy(scd.get_array_registration)
            if category == 'keys':
                return_object = deepcopy(scd.get_array_keys)
        elif performance_section == 'Host':
            if category == 'keys':
                return_object = deepcopy(scd.get_host_keys)
        elif performance_section == 'Initiator':
            if category == 'keys':
                return_object = deepcopy(scd.get_initiator_keys)
        elif performance_section == 'ISCSITarget':
            if category == 'keys':
                return_object = deepcopy(scd.get_iscsi_target_keys)
        elif performance_section == 'RDFA':
            if category == 'keys':
                return_object = deepcopy(scd.get_rdfa_keys)
        elif performance_section == 'RDFS':
            if category == 'keys':
                return_object = deepcopy(scd.get_rdfs_keys)

        return status_code, return_object

    @staticmethod
    def close():
        """close session."""


class FakeSplunkHelper(object):
    """Fake Splunk Helper."""

    def __init__(self):
        self.log_level = 'TEST'
        self.arg_mapping = {
            'u4v_ip_address': scd.U4P_IP_ADDRESS,
            'u4v_port': scd.U4P_PORT,
            'u4v_username': scd.U4P_USERNAME,
            'u4v_password': scd.U4P_PASSWORD,
            'u4v_vmax_id': scd.U4P_POWERMAX_ID_A,
            'rest_request_timeout': scd.U4P_REST_TIMEOUT,
            'enable_ssl': scd.U4P_ENABLE_SSL,
            'ssl_cert_location': scd.U4P_SSL_CERT_LOC,
            'interval': scd.SPLUNK_INTERVAL,
            'select_array': scd.SELECT_ARRAY,
            'select_srp': scd.SELECT_SRP,
            'select_sg': scd.SELECT_SG,
            'select_director': scd.SELECT_DIR,
            'select_port': scd.SELECT_PORT,
            'select_pg': scd.SELECT_PG,
            'select_iscsi': scd.SELECT_ISCSI,
            'select_host': scd.SELECT_HOST,
            'select_mv': scd.SELECT_MV,
            'select_initiator': scd.SELECT_INIT,
            'select_rdf': scd.SELECT_RDF,
            'select_metro_dr': scd.SELECT_METRO_DR,
            'select_snap_policy': scd.SELECT_SNAP_POLICY,
            'select_alerts': scd.SELECT_ALERTS,
            'select_audit_logs': scd.SELECT_AUDIT,
            'select_array_metrics': scd.SELECT_ARRAY_METRICS,
            'select_srp_metrics': scd.SELECT_SRP_METRICS,
            'select_sg_metrics': scd.SELECT_SG_METRICS,
            'select_fe_dir_metrics': scd.SELECT_FE_DIR_METRICS,
            'select_be_dir_metrics': scd.SELECT_BE_DIR_METRICS,
            'select_rdf_dir_metrics': scd.SELECT_RDF_DIR_METRICS,
            'select_im_dir_metrics': scd.SELECT_IM_DIR_METRICS,
            'select_eds_dir_metrics': scd.SELECT_EDS_DIR_METRICS,
            'select_fe_port_metrics': scd.SELECT_FE_PORT_METRICS,
            'select_be_port_metrics': scd.SELECT_BE_PORT_METRICS,
            'select_rdf_port_metrics': scd.SELECT_RDF_PORT_METRICS,
            'select_pg_metrics': scd.SELECT_PG_METRICS,
            'select_iscsi_target_metrics': scd.SELECT_ISCSI_TGT_METRICS,
            'select_ip_interface_metrics': scd.SELECT_IP_INTERFACE_METRICS,
            'select_host_metrics': scd.SELECT_HOST_METRICS,
            'select_initiator_metrics': scd.SELECT_INIT_METRICS,
            'select_mv_metrics': scd.SELECT_MV_METRICS,
            'select_rdfs_metrics': scd.SELECT_RDFS_METRICS,
            'select_rdfa_metrics': scd.SELECT_RDFA_METRICS}

    def get_arg(self, input_str):
        """Get a helper setting arg.

        :param input_str: arg to get -- str
        :returns: helper arg -- str/int/bool/list
        """
        return self.arg_mapping.get(input_str)

    def set_log_level(self, level):
        """Set log level.

        :param level: log level to be set -- str
        """
        self.log_level = level

    def get_log_level(self):
        """Get log level.

        :returns: log level -- str
        """
        return self.log_level

    @staticmethod
    def get_sourcetype():
        """Get Splunk source type.

        :returns: source type -- str
        """
        return scd.SPLUNK_SOURCE

    @staticmethod
    def get_output_index():
        """Get Splunk output index.

        :returns: output index -- str
        """
        return scd.SPLUNK_INDEX

    @staticmethod
    def log_error(msg):
        """Log (print) an error message.

        :param msg: log message -- str
        """
        print('CRITICAL: {}'.format(msg))

    @staticmethod
    def log_critical(msg):
        """Log (print) a critical message.

        :param msg: log message -- str
        """
        print('CRITICAL: {}'.format(msg))

    @staticmethod
    def log_warning(msg):
        """Log (print) a warning message.

        :param msg: log message -- str
        """
        print('WARNING: {}'.format(msg))

    @staticmethod
    def log_info(msg):
        """Log (print) an info message.

        :param msg: log message -- str
        """
        print('INFO: {}'.format(msg))

    @staticmethod
    def log_debug(msg):
        """Log (print) a debug message.

        :param msg: log message -- str
        """
        print('DEBUG: {}'.format(msg))

    @staticmethod
    def new_event(source, index, sourcetype, data):
        """Format data for writing to splunk index.

        :param source: data source -- str
        :param index: splunk index -- str
        :param sourcetype: data source type -- str
        :param data: data -- dict
        :returns: dummy event -- dict
        """
        return {'source': source, 'index': index, 'sourcetype': sourcetype,
                'data': data}


class FakeSplunkWriter(object):
    """Fake Splunk Writer."""

    def __init__(self):
        pass

    @staticmethod
    def write_event(self):
        """Write event dummy method."""
