"""bin/powermax_splunk_core/tests/unit_tests/test_powermax_input_module.py"""

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
from unittest import mock

from PyU4V import rest_requests
from PyU4V.utils import exception

from . import splunk_common_data
from . import splunk_fakes
from bin.powermax_splunk_core.driver import powermax_input_module
from bin.powermax_splunk_core.driver.powermax_splunk import PMaxSplunk


class PowerMaxInputModule(testtools.TestCase):
    """Test test_powermax_input_module.py"""

    def setUp(self):
        """setUp."""
        super().setUp()
        self.data = splunk_common_data.CommonData()
        self.helper = splunk_fakes.FakeSplunkHelper()
        self.writer = splunk_fakes.FakeSplunkWriter()
        # Reset all performance categories to false for individual testing
        for cat in self.data.HELPER_ARG_MAP_LIST:
            self.helper.arg_mapping[cat] = False

    @staticmethod
    def test_validate_input():
        """Test validate_input - coverage requirement only no return."""
        powermax_input_module.validate_input(helper=None, definition=None)

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_array_success(self, mck_write):
        """Test collect_events array level metrics success."""
        self.helper.arg_mapping['select_array'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.assert_called_once()

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_array_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_array_exception(self, mck_get, mck_log):
        """Test collect_events array level metrics exception."""
        self.helper.arg_mapping['select_array'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.assert_called_once()

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_srp_success(self, mck_write):
        """Test collect_events SRP level metrics success."""
        self.helper.arg_mapping['select_srp'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 2

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_srp_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_srp_exception(self, mck_get, mck_log):
        """Test collect_events SRP level metrics exception."""
        self.helper.arg_mapping['select_srp'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_storage_group_success(self, mck_write):
        """Test collect_events Storage Group level metrics success."""
        self.helper.arg_mapping['select_sg'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 2

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_storage_group_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_storage_group_exception(self, mck_get, mck_log):
        """Test collect_events Storage Group level metrics exception."""
        self.helper.arg_mapping['select_sg'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_director_success(self, mck_write):
        """Test collect_events director level metrics success."""
        self.helper.arg_mapping['select_director'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 5

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_director_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_director_exception(self, mck_get, mck_log):
        """Test collect_events director level metrics exception."""
        self.helper.arg_mapping['select_director'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 5

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_port_success(self, mck_write):
        """Test collect_events port level metrics success."""
        self.helper.arg_mapping['select_port'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 2

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_port_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_port_exception(self, mck_get, mck_log):
        """Test collect_events port level metrics exception."""
        self.helper.arg_mapping['select_port'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_port_group_success(self, mck_write):
        """Test collect_events Port Group level metrics success."""
        self.helper.arg_mapping['select_pg'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 2

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_port_group_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_port_group_exception(self, mck_get, mck_log):
        """Test collect_events Port Group level metrics exception."""
        self.helper.arg_mapping['select_pg'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_host_success(self, mck_write):
        """Test collect_events Host level metrics success."""
        self.helper.arg_mapping['select_host'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 2

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_host_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_host_exception(self, mck_get, mck_log):
        """Test collect_events Host level metrics exception."""
        self.helper.arg_mapping['select_host'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_initiator_success(self, mck_write):
        """Test collect_events initiator level metrics success."""
        self.helper.arg_mapping['select_initiator'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 2

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_initiator_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_initiator_exception(self, mck_get, mck_log):
        """Test collect_events initiator level metrics exception."""
        self.helper.arg_mapping['select_initiator'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_masking_view_success(self, mck_write):
        """Test collect_events masking_view level metrics success."""
        self.helper.arg_mapping['select_mv'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 2

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_masking_view_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_masking_view_exception(self, mck_get, mck_log):
        """Test collect_events masking_view level metrics exception."""
        self.helper.arg_mapping['select_mv'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_iscsi_success(self, mck_write):
        """Test collect_events iSCSI level metrics success."""
        self.helper.arg_mapping['select_iscsi'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 4

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_iscsi_target_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_iscsi_tgt_exception(self, mck_get, mck_log):
        """Test collect_events iSCSI level metrics exception."""
        self.helper.arg_mapping['select_iscsi'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_ip_interface_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_ip_interface_exception(self, mck_get, mck_log):
        """Test collect_events IP Interface level metrics exception."""
        self.helper.arg_mapping['select_iscsi'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_rdf_success(self, mck_write):
        """Test collect_events RDF level metrics success."""
        self.helper.arg_mapping['select_rdf'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 4

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_rdf_pair_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_rdf_inner_exception(self, mck_get, mck_log):
        """Test collect_events RDF level metrics exception."""
        self.helper.arg_mapping['select_rdf'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_rdf_group_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_rdf_outter_exception(self, mck_get, mck_log):
        """Test collect_events RDF level metrics exception."""
        self.helper.arg_mapping['select_rdf'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_metro_dr_success(self, mck_write):
        """Test collect_events Metro DR level metrics success."""
        self.helper.arg_mapping['select_metro_dr'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 4

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_metro_dr_environment_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_metro_dr_exception(self, mck_get, mck_log):
        """Test collect_events Metro DR level metrics exception."""
        self.helper.arg_mapping['select_metro_dr'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_snapshot_policy_success(self, mck_write):
        """Test collect_events Snapshot Policy level metrics success."""
        self.helper.arg_mapping['select_snap_policy'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 4

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_snapshot_policy_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_snapshot_policy_exception(self, mck_get, mck_log):
        """Test collect_events Snapshot Policy level metrics exception."""
        self.helper.arg_mapping['select_snap_policy'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_alert_success(self, mck_write):
        """Test collect_events Alert level metrics success."""
        self.helper.arg_mapping['select_alerts'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 4

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_alert',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_alert_exception(self, mck_get, mck_log):
        """Test collect_events Alert level metrics exception."""
        self.helper.arg_mapping['select_alerts'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'write_event')
    def test_collect_events_audit_logs_success(self, mck_write):
        """Test collect_events Audit Log level metrics success."""
        self.helper.arg_mapping['select_audit_logs'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_write.call_count = 4

    @mock.patch.object(PMaxSplunk, 'log_collection_error')
    @mock.patch.object(PMaxSplunk, 'get_audit_log_record_details',
                       side_effect=exception.ResourceNotFoundException)
    def test_collect_events_audit_logs_exception(self, mck_get, mck_log):
        """Test collect_events Audit Log level metrics exception."""
        self.helper.arg_mapping['select_audit_logs'] = True
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_log.call_count = 2

    @mock.patch.object(PMaxSplunk, 'process_collection_duration')
    @mock.patch.object(rest_requests.RestRequests, 'close_session')
    def test_collect_events_finish(self, mck_close, mck_process):
        """Test collect_events finish processes."""
        with mock.patch.object(
                rest_requests.RestRequests, 'establish_rest_session',
                return_value=splunk_fakes.FakeRequestsSession()):
            powermax_input_module.collect_events(
                helper=self.helper, ew=self.writer)
            mck_close.assert_called_once()
            mck_process.assert_called_once()
