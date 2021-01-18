"""bin/powermax_splunk_core/tests/unit_tests/test_powermax_splunk.py"""

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
import testtools
import time

from copy import deepcopy
from unittest import mock

from . import splunk_common_data
from . import splunk_fakes

from bin.powermax_splunk_core.driver.powermax_splunk import PMaxSplunk

from PyU4V import rest_requests
from PyU4V.utils import exception


class PowerMaxSplunkTest(testtools.TestCase):
    """Test powermax_splunk.py"""

    def setUp(self):
        """setUp."""
        super().setUp()
        self.data = splunk_common_data.CommonData()
        self.helper = splunk_fakes.FakeSplunkHelper()
        self.writer = splunk_fakes.FakeSplunkWriter()
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            self.spl = PMaxSplunk(helper=self.helper, event_writer=self.writer)
            self.conn = self.spl.conn
            self.rest_client = self.conn.rest_client

    def tearDown(self):
        """tearDown."""
        super().tearDown()

    def test_establish_pyu4v_connection(self):
        """Test _establish_pyu4v_connection default config."""
        # Check IP address & Port
        self.assertIn(self.data.U4P_IP_ADDRESS, self.rest_client.base_url)
        self.assertIn(self.data.U4P_PORT, self.rest_client.base_url)
        # Check Username & Password
        self.assertEqual(self.data.U4P_USERNAME, self.rest_client.username)
        self.assertEqual(self.data.U4P_PASSWORD, self.rest_client.password)
        # Check SSL Configuration
        self.assertEqual(self.data.U4P_SSL_CERT_LOC,
                         self.rest_client.verify_ssl)
        # Check REST timeout
        self.assertEqual(self.data.U4P_REST_TIMEOUT, self.rest_client.timeout)

    def test_establish_pyu4v_connection_ssl_true_no_path(self):
        """Test _establish_pyu4v_connection with SSL cert location set."""
        self.helper.arg_mapping['ssl_cert_location'] = None
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            temp_spl = PMaxSplunk(helper=self.helper, event_writer=self.writer)
            self.assertTrue(temp_spl.conn.rest_client.verify_ssl)

    def test_establish_pyu4v_connection_ssl_disabled(self):
        """Test _establish_pyu4v_connection with SSL disabled."""
        self.helper.arg_mapping['enable_ssl'] = False
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            temp_spl = PMaxSplunk(helper=self.helper, event_writer=self.writer)
            self.assertFalse(temp_spl.conn.rest_client.verify_ssl)

    def test_is_category_enabled_legacy_bool(self):
        """Test _is_category_enabled legacy config setting True."""
        self.helper.arg_mapping['select_array'] = True
        self.spl._set_enabled_metrics()
        self.assertTrue(self.spl.enabled_categories['array'])
        self.assertEqual('ALL', self.spl.enabled_metrics['array'])

    def test_set_enabled_metrics_variations(self):
        """Test _set_enabled_metrics with variations of config options."""
        self.helper.arg_mapping['select_array'] = True
        self.helper.arg_mapping['select_srp'] = 'srp_kpi'
        self.helper.arg_mapping['select_sg'] = 'sg_custom'
        self.helper.arg_mapping['select_sg_metrics'] = 'ResponseTime'

        self.spl._set_enabled_metrics()
        self.assertEqual('ALL', self.spl.enabled_metrics['array'])
        self.assertEqual('KPI', self.spl.enabled_metrics['srp'])
        self.assertIsInstance(self.spl.enabled_metrics['storage_group'], list)
        self.assertEqual(['ResponseTime'],
                         self.spl.enabled_metrics['storage_group'])

    def test_load_custom_metrics_invalid_metric_kpi_return(self):
        """Test _load_custom_metrics with no valid metrics, set default KPI."""
        self.helper.arg_mapping['select_sg'] = 'sg_custom'
        self.helper.arg_mapping['select_sg_metrics'] = 'FakeMetric'

        self.spl._set_enabled_metrics()
        self.assertEqual('KPI', self.spl.enabled_metrics['storage_group'])

    def test_load_custom_metrics_invalid_metric_in_list(self):
        """Test _load_custom_metrics with no valid metrics, set default KPI."""
        self.helper.arg_mapping['select_sg'] = 'sg_custom'
        self.helper.arg_mapping['select_sg_metrics'] = (
            'FakeMetric, ResponseTime')

        self.spl._set_enabled_metrics()
        self.assertIsInstance(self.spl.enabled_metrics['storage_group'], list)
        self.assertEqual(['ResponseTime'],
                         self.spl.enabled_metrics['storage_group'])

    def test_validate_configuration_invalid_interval(self):
        """Test _validate_configuration with invalid interval."""
        self.spl.interval = 299
        self.assertRaises(ValueError,
                          self.spl._validate_configuration)

        self.spl.interval = 301
        self.assertRaises(ValueError,
                          self.spl._validate_configuration)

    def test_validate_configuration_invalid_uni_version(self):
        """Test _validate_configuration with incorrect Unisphere version."""
        with mock.patch.object(self.spl.conn.common,
                               'get_uni_version', return_value=(None, 91)):
            self.assertRaises(EnvironmentError,
                              self.spl._validate_configuration)

    def test_validate_configuration_array_not_supported(self):
        """Test _validate_configuration with unsupported array (not V3+)."""
        with mock.patch.object(
                self.spl.conn.common, 'get_v3_or_newer_array_list',
                return_value=list()):
            self.assertRaises(EnvironmentError,
                              self.spl._validate_configuration)

    def test_validate_configuration_array_not_performance_registered(self):
        """Test _validate_configuration with array not perf registered."""
        with mock.patch.object(
                self.spl.perf, 'is_array_diagnostic_performance_registered',
                return_value=False):
            self.assertRaises(EnvironmentError,
                              self.spl._validate_configuration)

    def test_validate_configuration_timestamp_not_current(self):
        """Test _validate_configuration with array not perf registered."""
        time_now = int(time.time()) * 1000
        ten_minutes_ago = time_now - (self.data.ONE_MINUTE * 10)
        with mock.patch.object(
                self.spl.perf, 'get_last_available_timestamp',
                return_value=ten_minutes_ago):
            self.assertRaises(EnvironmentError,
                              self.spl._validate_configuration)

    def test_merge_dicts(self):
        """Test _merge_dicts with key from key consistency check."""
        dict_a = {'key_a': 'value_a', 'bei_os': 'value_b'}
        dict_b = {'key_b': 'value_c'}
        ref_dict = {'key_a': 'value_a', 'be_ios': 'value_b',
                    'key_b': 'value_c', 'array_id': self.spl.array_id,
                    'timestamp': self.spl.timestamp}

        return_dict = self.spl._merge_dicts(dict_a, dict_b)
        self.assertIsInstance(return_dict, str)
        self.assertEqual(ref_dict, json.loads(return_dict))

    def test_extract_nested_dicts(self):
        """Test _extract_nested_dicts."""
        nested_dict = {'key_a': {'nest_a': 'value_a', 'nest_b': 'value_b'}}
        ref_dict = {'key_a_nest_a': 'value_a', 'key_a_nest_b': 'value_b'}
        return_dict = self.spl._extract_nested_dicts(nested_dict)
        self.assertEqual(ref_dict, return_dict)

    def test_extract_nested_dicts_with_list(self):
        """Test _extract_nested_dicts with nested dict in list."""
        nested_dict = {'key_a': [{'nest_a': 'value_a', 'nest_b': 'value_b'}]}
        ref_dict = {'key_a_nest_a': 'value_a', 'key_a_nest_b': 'value_b'}
        return_dict = self.spl._extract_nested_dicts(nested_dict)
        self.assertEqual(ref_dict, return_dict)

    def test_extract_nested_dicts_no_nest(self):
        """Test _extract_nested_dicts no nested dicts present."""
        no_nest_dict = {'key_a': 'value_a', 'key_b': 'value_b'}
        return_dict = self.spl._extract_nested_dicts(no_nest_dict)
        self.assertEqual(no_nest_dict, return_dict)

    def test_extract_array_alert_summary(self):
        """Test _extract_array_alert_summary with array match."""
        summary_data = self.data.get_system_array_alerts
        ref_dict = {'array_performance_alert_alert_count': 4,
                    'array_alert_alert_count': 6}
        return_dict = self.spl._extract_array_alert_summary(summary_data)
        self.assertEqual(ref_dict, return_dict)

    def test_extract_array_alert_summary_no_match(self):
        """Test _extract_array_alert_summary with array no match."""
        summary_data = {
            "serverAlertSummary": {"alert_count": 0},
            "symmAlertSummary": [
                {"performanceAlertSummary": {"alert_count": 1},
                 "symmId": self.data.U4P_POWERMAX_ID_B,
                 "arrayAlertSummary": {"alert_count": 0}}]}
        ref_dict = {
            'array_alert_details': False,
            'array_alert_message': 'No Array alerts summary data available'}

        return_dict = self.spl._extract_array_alert_summary(summary_data)
        self.assertEqual(ref_dict, return_dict)

    def test_process_performance_response(self):
        """Test _process_performance_response."""
        time_now = int(time.time()) * 1000
        perf_data = {
            'result': [{'test_metric': 'test_value'}],
            'reporting_level': 'test_reporting_level',
            'timestamp': time_now}
        ref_perf_data = {
            'test_metric': 'test_value', 'timestamp': time_now}

        response = self.spl._process_performance_response(perf_data)
        self.assertIsInstance(response, dict)
        self.assertEqual(ref_perf_data, response)

    def test_write_event(self):
        """Test write_event."""
        data = 'test_data'
        with mock.patch.object(self.spl.ew, 'write_event') as we:
            with mock.patch.object(self.spl.helper, 'new_event') as ne:
                self.spl.write_event(data)
                we.assert_called_once()
                ne.assert_called_once_with(
                    source=self.spl.source, index=self.spl.index,
                    sourcetype=self.spl.source_type, data=data)

    def test_log_debug(self):
        """Test log_debug message."""
        with mock.patch.object(self.spl.helper, 'log_debug') as log:
            data = 'test_data'
            self.spl.log_debug(msg=data)
            log.assert_called_once_with('Input: {i} | Array: {a} | {m}'.format(
                i=self.spl.name, a=self.spl.array_id, m=data))

    def test_log_info(self):
        """Test log_info message."""
        with mock.patch.object(self.spl.helper, 'log_info') as log:
            data = 'test_data'
            self.spl.log_info(msg=data)
            log.assert_called_once_with('Input: {i} | Array: {a} | {m}'.format(
                i=self.spl.name, a=self.spl.array_id, m=data))

    def test_log_warning(self):
        """Test log_warning message."""
        with mock.patch.object(self.spl.helper, 'log_warning') as log:
            data = 'test_data'
            self.spl.log_warning(msg=data)
            log.assert_called_once_with('Input: {i} | Array: {a} | {m}'.format(
                i=self.spl.name, a=self.spl.array_id, m=data))

    def test_log_critical(self):
        """Test log_critical message."""
        with mock.patch.object(self.spl.helper, 'log_critical') as log:
            data = 'test_data'
            self.spl.log_critical(msg=data)
            log.assert_called_once_with('Input: {i} | Array: {a} | {m}'.format(
                i=self.spl.name, a=self.spl.array_id, m=data))

    def test_log_critical_with_exception(self):
        """Test log_critical message."""
        with mock.patch.object(self.spl.helper, 'log_critical') as log:
            data = 'test_data'
            self.assertRaises(ValueError,
                              self.spl.log_critical,
                              data, True, ValueError)
            log.assert_called_once_with('Input: {i} | Array: {a} | {m}'.format(
                i=self.spl.name, a=self.spl.array_id, m=data))

    def test_log_error(self):
        """Test log_error message."""
        with mock.patch.object(self.spl.helper, 'log_error') as log:
            data = 'test_data'
            self.spl.log_error(msg=data)
            log.assert_called_once_with('Input: {i} | Array: {a} | {m}'.format(
                i=self.spl.name, a=self.spl.array_id, m=data))

    def test_log_error_with_exception(self):
        """Test log_error message."""
        with mock.patch.object(self.spl.helper, 'log_error') as log:
            data = 'test_data'
            self.assertRaises(ValueError,
                              self.spl.log_error,
                              data, True, ValueError)
            log.assert_called_once_with('Input: {i} | Array: {a} | {m}'.format(
                i=self.spl.name, a=self.spl.array_id, m=data))

    def test_log_collection_error(self):
        """Test log_collection_error with params set."""
        asset_type = 'array'
        asset_id = self.data.U4P_POWERMAX_ID_A
        with mock.patch.object(self.spl, 'log_error') as le:
            self.spl.log_collection_error(asset_type=asset_type,
                                          asset_id=asset_id)
            le.assert_called_once()

    def test_process_collection_duration_success(self):
        """Test process_collection_duration with suitable interval."""
        time_now = int(time.time())
        end_time = time_now
        start_time = time_now - (60 * 4)
        with mock.patch.object(self.spl, 'log_info') as li:
            self.spl.process_collection_duration(start_time=start_time,
                                                 end_time=end_time)
            li.assert_called_once()

    def test_process_collection_duration_zero_result(self):
        """Test process_collection_duration with suitable interval."""
        time_now = int(time.time())
        end_time = time_now
        start_time = time_now
        with mock.patch.object(self.spl, 'log_info') as li:
            self.spl.process_collection_duration(start_time=start_time,
                                                 end_time=end_time)
            li.assert_called_once()

    def test_process_collection_duration_fail(self):
        """Test process_collection_duration with unsuitable interval."""
        time_now = int(time.time())
        end_time = time_now
        start_time = time_now - (60 * 6)
        with mock.patch.object(self.spl, 'log_critical') as li:
            self.spl.process_collection_duration(start_time=start_time,
                                                 end_time=end_time)
            li.assert_called_once()

    def test_get_array_details(self):
        """Test get_array_details success scenario."""
        ref_response = {
            'local': True,
            'device_count': 616, 'physical_capacity_used_capacity_gb': 1000.0,
            'physical_capacity_total_capacity_gb': 1000.0,
            'reporting_level': 'Array', 'all_flash': True, 'disk_count': 16,
            'system_sized_property_srp_name': 'SRP_1',
            'system_sized_property_sized_fba_capacity_tb': 69,
            'workload_detail_capable': True, 'storage_group_count': 5,
            'migration_session_count': 0, 'dm_source': True, 'dm_target': True,
            'rdf_capable': True, 'array_performance_alert_alert_count': 4,
            'array_alert_alert_count': 6, 'health_overall': 100.0,
            'health_service_level_compliance': 100.0,
            'array_id': self.data.U4P_POWERMAX_ID_A,
            'start_date': str(self.data.TIMESTAMP),
            'end_date': str(self.data.TIMESTAMP),
            'percent_busy': 0.027849833, 'timestamp': self.data.TIMESTAMP}

        array_response = self.spl.get_array_details()
        self.assertIsInstance(array_response, str)
        array_response = json.loads(array_response)
        self.assertEqual(ref_response, array_response)

    def test_get_array_details_no_slo_pro_data(self):
        """Test get_array_details no SLO provisioning data response."""
        with mock.patch.object(
                self.spl.conn.provisioning, 'get_array', return_value=dict()):
            array_response = self.spl.get_array_details()
            self.assertIsInstance(array_response, str)
            array_response = json.loads(array_response)
            self.assertIn('array_summary_details', array_response.keys())
            self.assertFalse(array_response['array_summary_details'])
            self.assertIn('array_summary_message', array_response.keys())
            self.assertIsInstance(array_response['array_summary_message'], str)

    def test_get_array_details_no_system_data(self):
        """Test get_array_details no system data response."""
        with mock.patch.object(
                self.spl.conn.common, 'get_array', return_value=dict()):
            array_response = self.spl.get_array_details()
            self.assertIsInstance(array_response, str)
            array_response = json.loads(array_response)
            self.assertIn('array_system_details', array_response.keys())
            self.assertFalse(array_response['array_system_details'])
            self.assertIn('array_system_message', array_response.keys())
            self.assertIsInstance(array_response['array_system_message'], str)

    def test_get_array_details_no_wlp_data(self):
        """Test get_array_details no WLP data response."""
        with mock.patch.object(
                self.spl.conn.wlp, 'get_capabilities', return_value=dict()):
            array_response = self.spl.get_array_details()
            self.assertIsInstance(array_response, str)
            array_response = json.loads(array_response)
            self.assertIn('array_wlp_details', array_response.keys())
            self.assertFalse(array_response['array_wlp_details'])
            self.assertIn('array_wlp_message', array_response.keys())
            self.assertIsInstance(array_response['array_wlp_message'], str)

    def test_get_array_details_no_migration_info_data(self):
        """Test get_array_details no migration info data response."""
        with mock.patch.object(
                self.spl.conn.migration, 'get_migration_info',
                return_value=dict()):
            array_response = self.spl.get_array_details()
            self.assertIsInstance(array_response, str)
            array_response = json.loads(array_response)
            self.assertIn('array_migration_details', array_response.keys())
            self.assertFalse(array_response['array_migration_details'])
            self.assertIn('array_migration_message', array_response.keys())
            self.assertIsInstance(
                array_response['array_migration_message'], str)

    def test_get_array_details_no_migration_capability_data(self):
        """Test get_array_details no migration capability data response."""
        with mock.patch.object(
                self.spl.conn.migration, 'get_array_migration_capabilities',
                return_value=dict()):
            array_response = self.spl.get_array_details()
            self.assertIsInstance(array_response, str)
            array_response = json.loads(array_response)
            self.assertIn(
                'array_migration_capabilities_detail', array_response.keys())
            self.assertFalse(
                array_response['array_migration_capabilities_detail'])
            self.assertIn(
                'array_migration_capabilities_message', array_response.keys())
            self.assertIsInstance(
                array_response['array_migration_capabilities_message'], str)

    def test_get_array_details_no_replication_capability_data(self):
        """Test get_array_details no replication capability data response."""
        with mock.patch.object(
                self.spl.conn.replication,
                'get_array_replication_capabilities', return_value=dict()):
            array_response = self.spl.get_array_details()
            self.assertIsInstance(array_response, str)
            array_response = json.loads(array_response)
            self.assertIn(
                'array_replication_capability_details', array_response.keys())
            self.assertFalse(
                array_response['array_replication_capability_details'])
            self.assertIn(
                'array_replication_capability_message', array_response.keys())
            self.assertIsInstance(
                array_response['array_replication_capability_message'], str)

    def test_get_array_details_no_health_data(self):
        """Test get_array_details no health data response."""
        with mock.patch.object(
                self.spl.conn.system, 'get_system_health',
                return_value=dict()):
            array_response = self.spl.get_array_details()
            self.assertIsInstance(array_response, str)
            array_response = json.loads(array_response)
            self.assertIn('array_health_details', array_response.keys())
            self.assertFalse(array_response['array_health_details'])
            self.assertIn('array_health_message', array_response.keys())
            self.assertIsInstance(array_response['array_health_message'], str)

    def test_get_array_details_no_alert_data(self):
        """Test get_array_details no alert data response."""
        with mock.patch.object(
                self.spl.conn.system, 'get_alert_summary',
                return_value=dict()):
            array_response = self.spl.get_array_details()
            self.assertIsInstance(array_response, str)
            array_response = json.loads(array_response)
            self.assertIn('array_alert_details', array_response.keys())
            self.assertFalse(array_response['array_alert_details'])
            self.assertIn('array_alert_message', array_response.keys())
            self.assertIsInstance(array_response['array_alert_message'], str)

    def test_get_array_details_no_performance_data(self):
        """Test get_array_details no performance data response."""
        with mock.patch.object(
                self.spl.perf, 'get_array_stats', return_value=dict()):
            array_response = self.spl.get_array_details()
            self.assertIsInstance(array_response, str)
            array_response = json.loads(array_response)
            self.assertIn('array_perf_details', array_response.keys())
            self.assertFalse(array_response['array_perf_details'])
            self.assertIn('array_perf_message', array_response.keys())
            self.assertIsInstance(array_response['array_perf_message'], str)

    def test_get_srp_details_success(self):
        """Test get_srp_details success scenario."""
        array_id = self.data.U4P_POWERMAX_ID_A
        srp_id = self.data.srp_id_a
        ref_response = {
            'num_of_disk_groups': 1, 'srp_id': srp_id,
            'srp_capacity_usable_total_tb': 24.45, 'reserved_cap_percent': 10,
            'srp_efficiency_overall_efficiency_ratio_to_one': 3179.4,
            'reporting_level': 'SRP', 'array_id': array_id,
            'start_date': str(self.data.TIMESTAMP),
            'end_date': str(self.data.TIMESTAMP),
            'percent_busy': 0.027849833, 'timestamp': self.data.TIMESTAMP}

        response = self.spl.get_srp_details(srp_id=srp_id)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(ref_response, response)

    def test_get_srp_details_no_performance_data(self):
        """Test get_srp_details no performance data available."""
        srp_id = self.data.srp_id_a
        with mock.patch.object(
                self.spl.perf, 'get_storage_resource_pool_stats',
                return_value=dict()):
            response = self.spl.get_srp_details(srp_id=srp_id)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['srp_perf_details'])
            self.assertIn('srp_perf_message', response.keys())
            self.assertIsInstance(response['srp_perf_message'], str)

    def test_get_storage_group_details_success(self):
        """Test get_storage_group_details success."""
        storage_group = self.data.storage_group_a
        ref_response = {
            'array_id': '000123456789', 'percent_busy': 0.027849833,
            'reporting_level': 'SG', 'slo_compliance': 'STABLE',
            'service_level': self.data.service_level_diamond,
            'srp': self.data.srp_id_a, 'storage_group_id': storage_group,
            'workload': 'NONE', 'start_date': str(self.data.TIMESTAMP),
            'end_date': str(self.data.TIMESTAMP),
            'timestamp': self.data.TIMESTAMP}

        response = self.spl.get_storage_group_details(
            storage_group_id=storage_group)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(ref_response, response)

    def test_get_storage_group_details_no_performance_data(self):
        """Test get_storage_group_details no performance data available."""
        storage_group = self.data.storage_group_a
        with mock.patch.object(
                self.spl.perf, 'get_storage_group_stats',
                return_value=dict()):
            response = self.spl.get_storage_group_details(
                storage_group_id=storage_group)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['sg_perf_details'])
            self.assertIn('sg_perf_message', response.keys())
            self.assertIsInstance(response['sg_perf_message'], str)

    def test_get_director_details_success(self):
        """Test get_director_details success."""
        director_list = [
            self.data.fe_director, self.data.be_director,
            self.data.rdf_director, self.data.im_director,
            self.data.eds_director]

        for dir_id in director_list:
            response = self.spl.get_director_details(director_id=dir_id)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertEqual(dir_id, response.get('director_id'))
            self.assertIn('percent_busy', response.keys())
            if any(x in dir_id for x in ['RF', 'RE']):
                self.assertIn('num_srdf_groups', response.keys())

    def test_get_director_details_unknown_dir_type(self):
        """Test get_director_details with unknown director type."""
        dir_id = 'XX-XX'
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.spl.get_director_details,
                          director_id=dir_id)

    def test_get_director_details_no_perf_data(self):
        """Test get_director_details no performance data available."""
        dir_id = self.data.fe_director
        with mock.patch.object(
                self.spl.perf, 'get_frontend_director_stats',
                return_value=dict()):
            response = self.spl.get_director_details(
                director_id=dir_id)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['dir_perf_details'])
            self.assertIn('dir_perf_message', response.keys())
            self.assertIsInstance(response['dir_perf_message'], str)

    def test_get_port_details_success(self):
        """Test get_port_details success scenario."""
        port_key_list = [
            self.data.fe_port_key, self.data.be_port_key,
            self.data.rdf_port_key]

        for port_key in port_key_list:
            response = self.spl.get_port_details(port_key=port_key)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertEqual(port_key.get('portId'),
                             response.get('port_id'))
            self.assertEqual(port_key.get('directorId'),
                             response.get('director_id'))
            self.assertNotIn('symmetrixPortKey', response.keys())
            self.assertIn('percent_busy', response.keys())
            self.assertIn('port_dir_type', response.keys())

    def test_get_port_details_invalid_port_type(self):
        """Test get_port_details with unknown port type."""
        port_key = {'directorId': 'XX-XX', 'portId': '1'}
        self.assertRaises(exception.VolumeBackendAPIException,
                          self.spl.get_port_details, port_key=port_key)

    def test_get_port_details_no_perf_data(self):
        """Test get_port_details no performance data available."""
        port_key = self.data.fe_port_key
        with mock.patch.object(
                self.spl.perf, 'get_frontend_port_stats',
                return_value=dict()):
            response = self.spl.get_port_details(port_key=port_key)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['port_perf_details'])
            self.assertIn('port_perf_message', response.keys())
            self.assertIsInstance(response['port_perf_message'], str)

    def test_get_port_group_details_success(self):
        """Test get_port_group_details success."""
        port_group = self.data.port_group_a
        response = self.spl.get_port_group_details(port_group_id=port_group)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(port_group, response.get('port_group_id'))
        self.assertEqual(['FA-1D:1'], response.get('port_list'))
        self.assertNotIn('symmetrixPortKey', response.keys())
        self.assertIn('percent_busy', response.keys())

    def test_get_port_group_details_no_perf_data(self):
        """Test get_port_details no performance data available."""
        port_group = self.data.port_group_a
        with mock.patch.object(
                self.spl.perf, 'get_port_group_stats',
                return_value=dict()):
            response = self.spl.get_port_group_details(
                port_group_id=port_group)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['pg_perf_details'])
            self.assertIn('pg_perf_message', response.keys())
            self.assertIsInstance(response['pg_perf_message'], str)

    def test_get_active_host_set(self):
        """Test get_active_host_set success."""
        response = self.spl.get_active_host_set()
        self.assertIsInstance(response, set)
        self.assertEqual({self.data.host_a, self.data.host_b},
                         response)

    def test_get_host_details_success(self):
        """Test get_host_details success."""
        host = self.data.host_a
        active_hosts = self.spl.get_active_host_set()

        response = self.spl.get_host_details(
            host_id=host, active_host_set=active_hosts)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(host, response.get('host_id'))
        self.assertEqual(['test_flag_a', 'test_flag_b'],
                         response.get('enabled_flags'))
        self.assertEqual([], response.get('disabled_flags'))
        self.assertTrue(response.get('performance_metrics'))

    def test_get_host_details_not_active(self):
        """Test get_host_details host not active no performance data."""
        host = self.data.host_a
        active_hosts = set()
        response = self.spl.get_host_details(
            host_id=host, active_host_set=active_hosts)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertFalse(response['host_perf_details'])
        self.assertFalse(response['performance_metrics'])
        self.assertIn('host_perf_message', response.keys())
        self.assertIsInstance(response['host_perf_message'], str)

    def test_get_host_details_no_performance_data(self):
        """Test get_host_details no performance data available."""
        host = self.data.host_a
        active_hosts = self.spl.get_active_host_set()
        with mock.patch.object(
                self.spl.perf, 'get_host_stats',
                return_value=dict()):
            response = self.spl.get_host_details(
                host_id=host, active_host_set=active_hosts)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['host_perf_details'])
            self.assertFalse(response['performance_metrics'])
            self.assertIn('host_perf_message', response.keys())
            self.assertIsInstance(response['host_perf_message'], str)

    def test_get_active_initiator_set(self):
        """Test get_active_host_set success."""
        response = self.spl.get_active_initiator_set()
        self.assertIsInstance(response, set)
        self.assertEqual({self.data.initiator_a, self.data.initiator_b},
                         response)

    def test_get_initiator_details_success(self):
        """Test get_initiator_details success."""
        initiator_id = self.data.dir_port_init_a
        active_inits = self.spl.get_active_initiator_set()
        response = self.spl.get_initiator_details(
            initiator_id=initiator_id, active_initiator_set=active_inits)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(self.data.initiator_a, response.get('initiator_id'))
        self.assertEqual(['test_flag_a', 'test_flag_b'],
                         response.get('flags_in_effect'))
        self.assertTrue(response.get('performance_metrics'))
        self.assertNotIn('symmetrixPortKey', response.keys())
        self.assertEqual(['{}:{}'.format(self.data.fe_director, '1')],
                         response.get('dir_port_keys'))

    def test_get_initiator_details_with_host_associated(self):
        """Test get_initiator_details with host associated."""
        initiator_id = self.data.dir_port_init_a
        active_inits = self.spl.get_active_initiator_set()
        with mock.patch.object(
                self.spl.conn.provisioning, 'get_initiator',
                return_value={'symmetrixPortKey': [self.data.fe_port_key],
                              'host': self.data.host_a}):
            response = self.spl.get_initiator_details(
                initiator_id=initiator_id, active_initiator_set=active_inits)
            response = json.loads(response)
            self.assertEqual(self.data.host_a, response.get('host_id'))

    def test_get_initiator_details_no_performance_data_iscsi(self):
        """Test get_initiator_details no performance data available - iSCSI."""
        initiator_id = self.data.dir_port_init_a
        active_inits = dict()
        with mock.patch.object(
                self.spl.conn.provisioning, 'get_initiator',
                return_value={
                    'symmetrixPortKey': [self.data.fe_port_key],
                    'initiatorId': self.data.initiator_a,
                    'type': 'iSCSI'}):
            response = self.spl.get_initiator_details(
                initiator_id=initiator_id, active_initiator_set=active_inits)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['initiator_perf_details'])
            self.assertFalse(response['performance_metrics'])
            self.assertIn('initiator_perf_message', response.keys())
            self.assertIsInstance(response['initiator_perf_message'], str)
            self.assertEqual('No iSCSI Initiator performance data available.',
                             response['initiator_perf_message'])

    def test_get_initiator_details_no_performance_data_not_active(self):
        """Test get_initiator_details no active performance data available."""
        initiator_id = self.data.dir_port_init_a
        active_inits = dict()
        with mock.patch.object(
                self.spl.conn.provisioning, 'get_initiator',
                return_value={
                    'symmetrixPortKey': [self.data.fe_port_key],
                    'initiatorId': self.data.initiator_a}):
            response = self.spl.get_initiator_details(
                initiator_id=initiator_id, active_initiator_set=active_inits)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['initiator_perf_details'])
            self.assertFalse(response['performance_metrics'])
            self.assertIn('initiator_perf_message', response.keys())
            self.assertIsInstance(response['initiator_perf_message'], str)
            self.assertEqual('No active Initiator performance data available.',
                             response['initiator_perf_message'])

    def test_get_initiator_details_no_performance_data(self):
        """Test get_initiator_details no performance data available."""
        initiator_id = self.data.dir_port_init_a
        active_inits = self.spl.get_active_initiator_set()
        with mock.patch.object(
                self.spl.perf, 'get_initiator_stats', return_value=dict()):
            response = self.spl.get_initiator_details(
                initiator_id=initiator_id, active_initiator_set=active_inits)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['initiator_perf_details'])
            self.assertFalse(response['performance_metrics'])
            self.assertIn('initiator_perf_message', response.keys())
            self.assertIsInstance(response['initiator_perf_message'], str)
            self.assertEqual('No Initiator performance data available.',
                             response['initiator_perf_message'])

    def test_get_masking_view_details_success_no_host_group(self):
        """Test get_masking_view_details success no host group associated."""
        masking_view = self.data.masking_view_a

        response = self.spl.get_masking_view_details(
            masking_view_id=masking_view)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(masking_view, response.get('masking_view_id'))
        self.assertNotEqual('None', response.get('host_id'))
        self.assertEqual('None', response.get('host_group_id'))
        self.assertIn('percent_busy', response.keys())
        self.assertIn('port_list', response.keys())

    def test_get_masking_view_details_success_no_host(self):
        """Test get_masking_view_details success no host associated."""
        masking_view = self.data.masking_view_a
        mck_response = deepcopy(self.data.get_masking_view_details)
        mck_response['hostGroupId'] = self.data.host_group_a
        mck_response.pop('hostId')

        with mock.patch.object(
                self.spl.conn.provisioning, 'get_masking_view',
                return_value=mck_response):
            response = self.spl.get_masking_view_details(
                masking_view_id=masking_view)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertEqual(masking_view, response.get('masking_view_id'))
            self.assertNotEqual('None', response.get('host_group_id'))
            self.assertEqual('None', response.get('host_id'))
            self.assertIn('percent_busy', response.keys())
            self.assertIn('port_list', response.keys())

    def test_get_masking_view_details_no_performance_data(self):
        """Test get_masking_view_details no performance data available."""
        masking_view = self.data.masking_view_a
        with mock.patch.object(
                self.spl.perf, 'get_masking_view_stats',
                return_value=dict()):
            response = self.spl.get_masking_view_details(
                masking_view_id=masking_view)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['mv_perf_details'])
            self.assertIn('mv_perf_message', response.keys())
            self.assertIsInstance(response['mv_perf_message'], str)

    def test_get_masking_view_connections(self):
        """Test get_masking_view_connections."""
        masking_view = self.data.masking_view_a
        mck_response = deepcopy(self.data.get_masking_view_details)
        mck_response.pop('hostId')
        with mock.patch.object(
                self.spl.conn.provisioning, 'get_masking_view',
                return_value=mck_response):

            response = self.spl.get_masking_view_connections(
                masking_view_id=masking_view)
            self.assertIsInstance(response, list)
            self.assertEqual(2, len(response))
            self.assertIsInstance(response[0], str)
            self.assertIsInstance(response[1], str)

            mv_conn_a = json.loads(response[0])
            mv_conn_b = json.loads(response[1])

            self.assertEqual('None', mv_conn_a.get('host_id'))
            self.assertEqual('None', mv_conn_a.get('host_group_id'))
            self.assertEqual(self.data.masking_view_a,
                             mv_conn_a.get('masking_view_id'))
            self.assertEqual('Masking View Connection',
                             mv_conn_a.get('reporting_level'))
            self.assertEqual('None', mv_conn_b.get('host_id'))
            self.assertEqual('None', mv_conn_b.get('host_group_id'))
            self.assertEqual('Masking View Connection',
                             mv_conn_b.get('reporting_level'))
            self.assertEqual(self.data.masking_view_a,
                             mv_conn_b.get('masking_view_id'))

    def test_get_ip_interface_list(self):
        """Test get_ip_interface_list."""
        mck_port_list = [
            {'directorId': self.data.iscsi_director, 'portId': '1'},
            {'directorId': self.data.iscsi_director, 'portId': '2'}]
        with mock.patch.object(
                self.spl.conn.provisioning, 'get_director_port_list',
                return_value=mck_port_list):
            response = self.spl.get_ip_interface_list()
            self.assertIsInstance(response, list)
            self.assertEqual(2, len(response))
            port_id = 0
            for ip_int in response:
                port_id += 1
                self.assertIsInstance(ip_int, dict)
                self.assertEqual(self.data.iscsi_director,
                                 ip_int.get('director_id'))
                self.assertEqual(str(port_id), ip_int.get('port_id'))
                self.assertEqual([self.data.ip_address_network_a,
                                  self.data.ip_address_network_b],
                                 ip_int.get('ip_interface_list'))

    def test_get_ip_interface_details_success(self):
        """Test get_ip_interface_details success"""
        mck_dir_port = {'symmetrixPort': {
            'identifier': self.data.iscsi_target_iqn_a}}
        director_id = self.data.iscsi_director
        interface_id = self.data.ip_address_network_a
        port_id = '1'

        with mock.patch.object(
                self.spl.conn.provisioning, 'get_director_port',
                return_value=mck_dir_port):
            response = self.spl.get_ip_interface_details(
                director_id=director_id, port_id=port_id,
                interface_id=interface_id)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertEqual(interface_id, response.get('ip_interface_id'))
            self.assertEqual(director_id, response.get('director_id'))
            self.assertEqual(port_id, response.get('port_id'))
            self.assertEqual(self.data.iscsi_target_iqn_a,
                             response.get('iscsi_target_iqn'))
            self.assertEqual(interface_id.split('-')[1],
                             response.get('network_id'))

    def test_get_ip_interface_details_no_iqn_no_performance_data(self):
        """Test get_ip_interface_details no IQN assigned & no perf data."""
        director_id = self.data.fe_director
        interface_id = self.data.ip_address_network_a
        port_id = '1'

        with mock.patch.object(
                self.spl.perf, 'get_ip_interface_stats', return_value=dict()):
            response = self.spl.get_ip_interface_details(
                director_id=director_id, port_id=port_id,
                interface_id=interface_id)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertEqual('None', response.get('iscsi_target_iqn'))
            self.assertFalse(response['ip_interface_perf_details'])
            self.assertIn('ip_interface_perf_message', response.keys())
            self.assertIsInstance(response['ip_interface_perf_message'], str)

    def test_get_iscsi_target_list(self):
        """Test get_iscsi_target_list."""
        with mock.patch.object(
                self.spl.conn.provisioning, 'get_port_list',
                side_effect=self.spl.conn.provisioning.get_port_list) as mck_g:
            response = self.spl.get_iscsi_target_list()
            mck_g.assert_called_once_with(
                filters={'iscsi_target': True})
            self.assertEqual([self.data.iscsi_port_key], response)

    def test_get_iscsi_target_details_success(self):
        """Test get_iscsi_target_details."""
        port_key = self.data.iscsi_port_key
        response = self.spl.get_iscsi_target_details(port_key=port_key)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(self.data.iscsi_target_iqn_a,
                         response.get('identifier'))

    def test_get_iscsi_target_details_no_performance_data(self):
        """Test get_iscsi_target_details no performance data available."""
        port_key = self.data.iscsi_port_key
        with mock.patch.object(
                self.spl.perf, 'get_iscsi_target_stats', return_value=dict()):
            response = self.spl.get_iscsi_target_details(port_key=port_key)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertIn('iscsi_tgt_perf_details', response.keys())
            self.assertFalse(response['iscsi_tgt_perf_details'])
            self.assertIn('iscsi_tgt_perf_message', response.keys())
            self.assertIsInstance(response['iscsi_tgt_perf_message'], str)

    def test_get_rdf_group_map_success(self):
        """Test get_rdf_group_map success for both RDF/A & RDF/S"""
        ref_response = {
            '1': {'label': 'label_1', 'sync_perf': False, 'async_perf': True},
            '2': {'label': 'label_2', 'sync_perf': False, 'async_perf': True},
            '3': {'label': 'label_3', 'sync_perf': True, 'async_perf': False},
            '4': {'label': 'label_4', 'sync_perf': True, 'async_perf': False}}

        response = self.spl.get_rdf_group_map()
        self.assertIsInstance(response, dict)
        self.assertEqual(ref_response, response)

    def test_get_rdf_group_map_no_sync_groups(self):
        """Test get_rdf_group_map_success no RDF/S groups configured."""
        ref_response = {
            '1': {'label': 'label_1', 'sync_perf': False, 'async_perf': True},
            '2': {'label': 'label_2', 'sync_perf': False, 'async_perf': True},
            '3': {'label': 'label_3', 'sync_perf': False, 'async_perf': False},
            '4': {'label': 'label_4', 'sync_perf': False, 'async_perf': False}}
        with mock.patch.object(
                self.spl.perf, 'get_rdfs_keys',
                side_effect=exception.ResourceNotFoundException):
            response = self.spl.get_rdf_group_map()
            self.assertIsInstance(response, dict)
            self.assertEqual(ref_response, response)

    def test_get_rdf_group_map_no_async_groups(self):
        """Test get_rdf_group_map_success no RDF/A groups configured."""
        ref_response = {
            '1': {'label': 'label_1', 'sync_perf': False, 'async_perf': False},
            '2': {'label': 'label_2', 'sync_perf': False, 'async_perf': False},
            '3': {'label': 'label_3', 'sync_perf': True, 'async_perf': False},
            '4': {'label': 'label_4', 'sync_perf': True, 'async_perf': False}}
        with mock.patch.object(
                self.spl.perf, 'get_rdfa_keys',
                side_effect=exception.ResourceNotFoundException):
            response = self.spl.get_rdf_group_map()
            self.assertIsInstance(response, dict)
            self.assertEqual(ref_response, response)

    def test_get_rdf_group_details_sync_group_success(self):
        """Test get_rdf_group_details sync group."""
        rdf_map = self.spl.get_rdf_group_map()
        rdf_group = '3'

        response = self.spl.get_rdf_group_details(
            rdf_group_number=rdf_group, rdf_group_map=rdf_map)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertTrue(response.get('rdfs'))
        self.assertIn('percent_busy', response.keys())

    def test_get_rdf_group_details_async_group_success(self):
        """Test get_rdf_group_details async group."""
        rdf_map = self.spl.get_rdf_group_map()
        rdf_group = '1'

        response = self.spl.get_rdf_group_details(
            rdf_group_number=rdf_group, rdf_group_map=rdf_map)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertTrue(response.get('rdfa'))
        self.assertIn('percent_busy', response.keys())

    def test_get_rdf_group_details_no_performance_data(self):
        """Test get_rdf_group_details no performance data available."""
        rdf_map = self.spl.get_rdf_group_map()
        rdf_group = '1'

        with mock.patch.object(
                self.spl.perf, 'get_rdfa_stats', return_value=dict()):
            response = self.spl.get_rdf_group_details(
                rdf_group_number=rdf_group, rdf_group_map=rdf_map)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertFalse(response['rdfg_perf_details'])
            self.assertIn('rdfg_perf_message', response.keys())
            self.assertIsInstance(response['rdfg_perf_message'], str)

    def test_get_rdf_pair_details_success(self):
        """Test get_rdf_pair_details success."""
        volume_id = self.data.volume_a
        rdf_map = self.spl.get_rdf_group_map()
        rdf_group = '1'
        rdfg_data = self.spl.get_rdf_group_details(
            rdf_group_number=rdf_group, rdf_group_map=rdf_map)

        response = self.spl.get_rdf_pair_details(rdfg_data=rdfg_data,
                                                 device_id=volume_id)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertIn('type', response.keys())
        self.assertIn('rdfg_label', response.keys())
        self.assertIn('local_volume_name', response.keys())
        self.assertIn('remote_volume_name', response.keys())

    def test_get_metro_dr_environment_details_success(self):
        """Test get_metro_dr_environment_details success."""

        metro_dr_name = 'env-1'
        response = self.spl.get_metro_dr_environment_details(
            metro_dr_env_name=metro_dr_name)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(metro_dr_name, response.get('name'))
        self.assertNotIn(' ', response.get('environment_state'))
        self.assertNotIn(',', response.get('environment_state'))
        self.assertNotIn(' ', response.get('dr_rdf_mode'))
        self.assertNotIn(',', response.get('dr_rdf_mode'))

    def test_get_snapshot_policy_details_cloud(self):
        """Test get_snapshot_policy_details success."""
        policy_name = 'test_policy'
        response = self.spl.get_snapshot_policy_details(
            snap_policy_name=policy_name)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(policy_name, response.get('name'))
        self.assertEqual('cloud', response.get('policy_type'))

    def test_get_snapshot_policy_details_local(self):
        """Test get_snapshot_policy_details success."""
        policy_name = 'test_policy'
        mock_response = self.data.get_snapshot_policy_details
        mock_response.pop('provider_name')
        with mock.patch.object(
                self.spl.conn.snapshot_policy, 'get_snapshot_policy',
                return_value=mock_response):
            response = self.spl.get_snapshot_policy_details(
                snap_policy_name=policy_name)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertEqual('local', response.get('policy_type'))
            self.assertEqual('N/A', response.get('provider_name'))

    def test_get_alert_list(self):
        """Test get_alert_list success."""
        response = self.spl.get_alert_list()
        ref_response = self.data.get_system_alert_list.get('alertId')
        self.assertIsInstance(response, list)
        self.assertEqual(ref_response, response)

    def test_get_alert(self):
        """Test get_alert."""
        alert_id = 'test-0001'
        response = self.spl.get_alert(alert_id=alert_id)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual(alert_id, response.get('alert_id'))
        self.assertIn('array_id', response.keys())
        self.assertIn('asset_id', response.keys())
        self.assertIn('timestamp', response.keys())
        self.assertIn('u4v_source', response.keys())

    def test_get_audit_log_record_list(self):
        """Test get_audit_log_record_list."""
        rest_response = self.data.get_audit_log_list
        ref_response = [
            x.get('record_id') for x in rest_response['resultList']['result']]
        response = self.spl.get_audit_log_record_list()
        self.assertIsInstance(response, list)
        self.assertEqual(ref_response, response)

    def test_get_audit_log_record_details(self):
        """Test get_audit_log_record_details."""
        record_id = '10000'
        response = self.spl.get_audit_log_record_details(record_id=record_id)
        self.assertIsInstance(response, str)
        response = json.loads(response)
        self.assertEqual('None', response.get('activity_id'))
        self.assertIn('/', response.get('username'))
        self.assertNotEqual(' ', response.get('message')[-1])
        self.assertEqual(13, len(str(response.get('timestamp'))))

    def test_get_audit_log_record_details_no_username(self):
        """Test get_audit_log_record_details."""
        record_id = '10000'
        mock_response = self.data.get_audit_log
        mock_response.pop('username')
        with mock.patch.object(
                self.spl.conn.system, 'get_audit_log_record',
                return_value=mock_response):
            response = self.spl.get_audit_log_record_details(
                record_id=record_id)
            self.assertIsInstance(response, str)
            response = json.loads(response)
            self.assertEqual('None', response.get('username'))
