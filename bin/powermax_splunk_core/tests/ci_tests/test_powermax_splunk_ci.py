"""bin/powermax_splunk_core/tests/ci_tests/test_powermax_splunk_ci.py"""

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

import testtools

from . import base

from bin.powermax_splunk_core.driver import powermax_input_module
from bin.powermax_splunk_core.driver.utils import powermax_constants as pc

ALL = 'metrics_all'
KPI = 'metrics_kpi'
CUSTOM = 'metrics_custom'


class CITestPowerMaxSplunk(base.TestBaseTestCase, testtools.TestCase):
    """Test PowerMax Splunk."""

    # Array level tests
    def test_collect_events_array_legacy_all(self):
        """Test collect_events for array with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.ARRAY)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.ARRAY, reporting_level='Array', metric_type=ALL)

    def test_collect_events_array_all(self):
        """Test collect_events for array with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'array_all' if (
                k == pc.ARRAY) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.ARRAY, reporting_level='Array', metric_type=ALL)

    def test_collect_events_array_kpi(self):
        """Test collect_events for array with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'array_kpi' if (
                k == pc.ARRAY) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.ARRAY, reporting_level='Array', metric_type=KPI)

    def test_collect_events_array_custom(self):
        """Test collect_events for array with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'array_custom' if (
                k == pc.ARRAY) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.ARRAY, reporting_level='Array', metric_type=CUSTOM)

    # SRP level tests
    def test_collect_events_srp_legacy_all(self):
        """Test collect_events for SRP with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.SRP)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.SRP, reporting_level='SRP', metric_type=ALL)

    def test_collect_events_srp_all(self):
        """Test collect_events for SRP with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'srp_all' if (
                k == pc.SRP) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.SRP, reporting_level='SRP', metric_type=ALL)

    def test_collect_events_srp_kpi(self):
        """Test collect_events for SRP with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'srp_kpi' if (
                k == pc.SRP) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.SRP, reporting_level='SRP', metric_type=KPI)

    def test_collect_events_srp_custom(self):
        """Test collect_events for SRP with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'srp_custom' if (
                k == pc.SRP) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.SRP, reporting_level='SRP', metric_type=CUSTOM)

    # Storage Group level tests
    def test_collect_events_storage_group_legacy_all(self):
        """Test collect_events for SG with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.STORAGE_GROUP)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.STORAGE_GROUP, reporting_level='SG', metric_type=ALL)

    def test_collect_events_storage_group_all(self):
        """Test collect_events for SG with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'sg_all' if (
                k == pc.STORAGE_GROUP) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.STORAGE_GROUP, reporting_level='SG', metric_type=ALL)

    def test_collect_events_storage_group_kpi(self):
        """Test collect_events for SG with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'sg_kpi' if (
                k == pc.STORAGE_GROUP) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.STORAGE_GROUP, reporting_level='SG', metric_type=KPI)

    def test_collect_events_storage_group_custom(self):
        """Test collect_events for SG with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'sg_custom' if (
                k == pc.STORAGE_GROUP) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.STORAGE_GROUP, reporting_level='SG', metric_type=CUSTOM)

    # Director level tests
    def test_collect_events_director_legacy_all(self):
        """Test collect_events for Director with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.DIRECTOR)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_director_event_collection_asserts(metric_type=ALL)

    def test_collect_events_director_all(self):
        """Test collect_events for Director with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'dir_all' if (
                k == pc.DIRECTOR) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_director_event_collection_asserts(metric_type=ALL)

    def test_collect_events_director_kpi(self):
        """Test collect_events for Director with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'dir_kpi' if (
                k == pc.DIRECTOR) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_director_event_collection_asserts(metric_type=KPI)

    def test_collect_events_director_custom(self):
        """Test collect_events for Director with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'dir_custom' if (
                k == pc.DIRECTOR) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_director_event_collection_asserts(metric_type=CUSTOM)

    # Port level tests
    def test_collect_events_port_legacy_all(self):
        """Test collect_events for Port with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.PORT)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_port_event_collection_asserts(metric_type=ALL)

    def test_collect_events_port_all(self):
        """Test collect_events for Port with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'port_all' if k == pc.PORT else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_port_event_collection_asserts(metric_type=ALL)

    def test_collect_events_port_kpi(self):
        """Test collect_events for Port with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'port_kpi' if k == pc.PORT else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_port_event_collection_asserts(metric_type=KPI)

    def test_collect_events_port_custom(self):
        """Test collect_events for Port with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'port_custom' if (
                k == pc.PORT) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_port_event_collection_asserts(metric_type=CUSTOM)

    # Port Group level tests
    def test_collect_events_port_group_legacy_all(self):
        """Test collect_events for PG with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.PORT_GROUP)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.PORT_GROUP, reporting_level='Port Group',
            metric_type=ALL)

    def test_collect_events_port_group_all(self):
        """Test collect_events for PG with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'pg_all' if (
                k == pc.PORT_GROUP) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.PORT_GROUP, reporting_level='Port Group',
            metric_type=ALL)

    def test_collect_events_port_group_kpi(self):
        """Test collect_events for PG with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'pg_kpi' if (
                k == pc.PORT_GROUP) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.PORT_GROUP, reporting_level='Port Group',
            metric_type=KPI)

    def test_collect_events_port_group_custom(self):
        """Test collect_events for PG with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'pg_custom' if (
                k == pc.PORT_GROUP) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.PORT_GROUP, reporting_level='Port Group',
            metric_type=CUSTOM)

    # Host level tests
    def test_collect_events_host_legacy_all(self):
        """Test collect_events for Host with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.HOST)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_active_inactive_event_collection_asserts(metric_type=ALL)

    def test_collect_events_host_all(self):
        """Test collect_events for Host with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'host_all' if (
                k == pc.HOST) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_active_inactive_event_collection_asserts(metric_type=ALL)

    def test_collect_events_host_kpi(self):
        """Test collect_events for Host with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'host_kpi' if (
                k == pc.HOST) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_active_inactive_event_collection_asserts(metric_type=KPI)

    def test_collect_events_host_custom(self):
        """Test collect_events for Host with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'host_custom' if (
                k == pc.HOST) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_active_inactive_event_collection_asserts(metric_type=CUSTOM)

    # Initiator level tests
    def test_collect_events_initiator_legacy_all(self):
        """Test collect_events for Initiator with legacy True setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.INITIATOR)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_active_inactive_event_collection_asserts(map_key=pc.INITIATOR,
                                                          metric_type=ALL)

    def test_collect_events_initiator_all(self):
        """Test collect_events for Initiator with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'init_all' if (
                k == pc.INITIATOR) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_active_inactive_event_collection_asserts(map_key=pc.INITIATOR,
                                                          metric_type=ALL)

    def test_collect_events_initiator_kpi(self):
        """Test collect_events for Initiator with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'init_kpi' if (
                k == pc.INITIATOR) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_active_inactive_event_collection_asserts(map_key=pc.INITIATOR,
                                                          metric_type=KPI)

    def test_collect_events_initiator_custom(self):
        """Test collect_events for Initiator with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'init_custom' if (
                k == pc.INITIATOR) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_active_inactive_event_collection_asserts(map_key=pc.INITIATOR,
                                                          metric_type=CUSTOM)

    # Masking View level tests
    def test_collect_events_masking_view_legacy_all(self):
        """Test collect_events for MV with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.MASKING_VIEW)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_masking_view_event_collection_asserts(metric_type=ALL)

    def test_collect_events_masking_view_all(self):
        """Test collect_events for MV with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'mv_all' if (
                k == pc.MASKING_VIEW) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_masking_view_event_collection_asserts(metric_type=ALL)

    def test_collect_events_masking_view_kpi(self):
        """Test collect_events for MV with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'mv_kpi' if (
                k == pc.MASKING_VIEW) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_masking_view_event_collection_asserts(metric_type=KPI)

    def test_collect_events_masking_view_custom(self):
        """Test collect_events for MV with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'mv_custom' if (
                k == pc.MASKING_VIEW) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_masking_view_event_collection_asserts(metric_type=CUSTOM)

    # iSCSI level tests
    def test_collect_events_iscsi_legacy_all(self):
        """Test collect_events for iSCSI with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.ISCSI)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_iscsi_event_collection_asserts(metric_type=ALL)

    def test_collect_events_iscsi_all(self):
        """Test collect_events for iSCSI with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'iscsi_all' if (
                k == pc.ISCSI) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_iscsi_event_collection_asserts(metric_type=ALL)

    def test_collect_events_iscsi_kpi(self):
        """Test collect_events for iSCSI with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'iscsi_kpi' if (
                k == pc.ISCSI) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_iscsi_event_collection_asserts(metric_type=KPI)

    def test_collect_events_iscsi_custom(self):
        """Test collect_events for iSCSI with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'iscsi_custom' if (
                k == pc.ISCSI) else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_iscsi_event_collection_asserts(metric_type=CUSTOM)

    # RDFG level tests
    def test_collect_events_rdfg_legacy_all(self):
        """Test collect_events for RDFGs with legacy True config setting."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.RDF)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_rdfg_event_collection_asserts(metric_type=ALL)

    def test_collect_events_rdfg_all(self):
        """Test collect_events for RDFGs with 'ALL' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'rdf_all' if k == pc.RDF else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_rdfg_event_collection_asserts(metric_type=ALL)

    def test_collect_events_rdfg_kpi(self):
        """Test collect_events for RDFGs with 'KPI' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'rdf_kpi' if k == pc.RDF else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_rdfg_event_collection_asserts(metric_type=KPI)

    def test_collect_events_rdfg_custom(self):
        """Test collect_events for RDFGs with 'custom' metrics enabled."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'rdf_custom' if k == pc.RDF else False

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_rdfg_event_collection_asserts(metric_type=CUSTOM)

    # Metro DR
    def test_collect_events_metro_dr(self):
        """Test collect_events for Metro DR."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.METRO_DR)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        event_data = self.load_event_data()
        event, __ = self.load_event(event_data[0])

        self.assertEqual('Metro DR', event.get('reporting_level'))
        if event.get('environment_state'):
            self.assertNotIn(',', event.get('environment_state'))
            self.assertNotIn(' ', event.get('environment_state'))
        if event.get('dr_rdf_mode'):
            self.assertNotIn(',', event.get('dr_rdf_mode'))
            self.assertNotIn(' ', event.get('dr_rdf_mode'))

    # Snapshot Policies
    def test_collect_events_snapshot_policy(self):
        """Test collect_events for Snapshot Policies."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.SNAP_POLICY)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        event_data = self.load_event_data()
        event, event_keys = self.load_event(event_data[0])

        self.assertEqual('Snapshot Policy', event.get('reporting_level'))
        self.assertIn('policy_type', event_keys)
        self.assertIn('provider_name', event_keys)

    # Alerts
    def test_collect_events_alerts(self):
        """Test collect_events for Alerts."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.ALERTS)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        event_data = self.load_event_data()
        event, event_keys = self.load_event(event_data[0])

        self.assertEqual('Alert', event.get('reporting_level'))
        self.assertIn('array_id', event_keys)
        self.assertIn('asset_id', event_keys)
        self.assertIn('u4v_source', event_keys)

    # Audit Logs
    def test_collect_events_audit_logs(self):
        """Test collect_events for Audit Logs."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = bool(k == pc.AUDIT_LOGS)

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        event_data = self.load_event_data()
        event, event_keys = self.load_event(event_data[0])

        self.assertEqual('Audit Log', event.get('reporting_level'))
        self.assertIn('username', event_keys)
        self.assertIn('activity_id', event_keys)
        self.assertNotIn('\\', event.get('username'))
        self.assertNotEqual(' ', event.get('message')[-1])
        self.assertEqual(13, len(str(event.get('timestamp'))))

    # Misc
    def test_collect_events_invalid_metric_all_invalid_use_kpi(self):
        """Test collect_events with all invalid metric use KPI."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'array_custom' if (
                k == pc.ARRAY) else False
        self.helper.arg_mapping['select_array_metrics'] = 'FakeMetric'

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        self.run_standard_event_collection_asserts(
            map_key=pc.ARRAY, reporting_level='Array', metric_type=KPI)

    def test_collect_events_invalid_metric_single(self):
        """Test collect_events with invalid metric remove from list."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = 'array_custom' if (
                k == pc.ARRAY) else False
        self.helper.arg_mapping['select_array_metrics'] = (
            'BEReqs, HostIOs, FakeMetric')

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        event_data = self.load_event_data()
        event, event_keys = self.load_event(event_data[0])

        self.assertIn('be_reqs', event_keys)
        self.assertIn('host_ios', event_keys)
        self.assertNotIn('FakeMetric', event_keys)
        self.assertNotIn('fake_metric', event_keys)

    def test_full_clean_run_all_reporting_levels_all_metrics(self):
        """Test collect_events with everything enabled and all metrics."""
        for k, v in pc.REPORTING_LEVELS_KEY_MAP.items():
            self.helper.arg_mapping[v] = True

        powermax_input_module.collect_events(
            helper=self.helper, ew=self.writer)
        event_data = self.load_event_data()

        for event in event_data:
            event, event_keys = self.load_event(event)
            self.assertIn('reporting_level', event_keys)
            self.assertIn('timestamp', event_keys)
            self.assertIn('array_id', event_keys)
