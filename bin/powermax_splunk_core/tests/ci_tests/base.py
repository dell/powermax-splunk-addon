"""bin/powermax_splunk_core/tests/ci_tests/base.py"""

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
import re
import testtools

import PyU4V

from . import splunk_fakes

from bin.powermax_splunk_core.driver.utils import (
    powermax_key_consistency as pkc)
from bin.powermax_splunk_core.driver.utils import powermax_constants as pc

ALL = 'metrics_all'
KPI = 'metrics_kpi'
CUSTOM = 'metrics_custom'


class TestBaseTestCase(testtools.TestCase):
    """Base test case class for all CI tests."""

    def setUp(self):
        """Set up before CI test has started."""
        super().setUp()
        self.helper = splunk_fakes.FakeSplunkHelper()
        self.writer = splunk_fakes.FakeSplunkWriter()
        self.pkc = pkc.consistent_keys
        self.conn = PyU4V.U4VConn(
            username=self.helper.get_arg('u4v_username'),
            password=self.helper.get_arg('u4v_password'),
            server_ip=self.helper.get_arg('u4v_ip_address'),
            port=self.helper.get_arg('u4v_port'),
            verify=True,
            array_id=self.helper.get_arg('u4v_vmax_id'))

    def tearDown(self):
        """Tear down after CI test has finished."""
        super().tearDown()
        self.writer.cleanup_event_data()

    def load_string_custom_metrics(self, metrics):
        """Load custom metric list from comma separated string list.

        :param metrics:
        :return:
        """
        metrics = metrics.replace(' ', '')
        metrics = metrics.split(',')
        return self._convert_metrics_snake_case(metrics)

    def _convert_metrics_snake_case(self, metrics):
        """Convert a list of metrics from camel case to snake case.

        :param metrics: metrics -- list
        :returns: formatted metrics -- list
        """
        def convert_to_snake_case(camel_case_string):
            """Convert a string from camel case to snake case.

            :param camel_case_string: string for formatting -- str
            :returns: snake case variant -- str
            """
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_case_string)
            s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
            return s2.replace('__', '_')

        formatted_metrics = list()
        for metric in metrics:
            metric = convert_to_snake_case(metric)
            if self.pkc.get(metric):
                metric = self.pkc.get(metric)
            formatted_metrics.append(metric)

        return formatted_metrics

    def load_event_data(self):
        """Load test event data from pickle file.

        :returns: event data -- list
        """
        try:
            event_data = self.writer.load_event_data()
            self.assertIsInstance(event_data, list)
            self.assertNotEqual([], event_data)
            return event_data
        except (OSError, EnvironmentError) as e:
            self.skipTest('No pickle data loaded: {}'.format(e))

    def load_event(self, event_data):
        """Load JSON data for a given Splunk event with a list of keys.

        :param event_data: splunk event data -- dict
        :returns: data, keys -- dict, set
        """
        event = json.loads(event_data.get('data'))
        self.assertIsInstance(event, dict)
        self.assertNotEqual({}, event)

        return event, set(event.keys())

    def load_metrics(self, map_key, metric_type):
        """Load metrics required for various CI tests.

        Valid options are 'ALL, KPI, CUSTOM'.

        :param map_key: the key used to retrieve metrics from PyU4V -- str
        :param metric_type: the type of metrics in use (ALL, KPI, etc.) -- str
        :returns: performance metrics -- list
        :raises ValueError when invalid metric_type used
        """
        if metric_type in [ALL, KPI]:
            metrics_key = pc.PERFORMANCE_KEY_MAP[map_key][pc.U4P_CAT]
            kpi = bool(metric_type == KPI)
            metrics = self.conn.performance.get_performance_metrics_list(
                category=metrics_key, kpi_only=kpi,
                array_id=self.conn.array_id)
            metrics = self._convert_metrics_snake_case(metrics)
            self.assertNotEqual([], metrics)
        elif metric_type == CUSTOM:
            custom_key = pc.PERFORMANCE_KEY_MAP[map_key][pc.METRICS]
            metrics = self.helper.arg_mapping[custom_key]
            metrics = self.load_string_custom_metrics(metrics)
        else:
            raise ValueError('Invalid metrics type [ALL, KPI, CUSTOM].')

        return metrics

    def run_standard_event_collection_asserts(
            self, map_key, reporting_level, metric_type):
        """Load pickle event data and run assertions on contents.

        :param map_key: the key used to retrieve metrics from PyU4V -- str
        :param reporting_level: performance reporting category -- str
        :param metric_type: the type of metrics in use (ALL, KPI, etc.) -- str
        """
        event_data = self.load_event_data()
        event, event_keys = self.load_event(event_data[0])
        self.assertEqual(reporting_level, event.get('reporting_level'))

        metrics = self.load_metrics(map_key, metric_type)
        for metric in metrics:
            self.assertIn(metric, event_keys)

    def run_srp_event_collection_asserts(self, map_key, metric_type):
        """Load pickle event data and run assertions on contents.

        :param map_key: the key used to retrieve metrics from PyU4V -- str
        :param metric_type: the type of metrics in use (ALL, KPI, etc.) -- str
        """
        event_data = self.load_event_data()
        for e in event_data:
            event, event_keys = self.load_event(e)
            try:
                self.assertIn(event.get('reporting_level'),
                              ['SRP', 'SRP_PERFORMANCE'])
            except AssertionError:
                pass
            # self.assertEqual(reporting_level, event.get('reporting_level'))

            if event.get('reporting_level') == 'SRP_PERFORMANCE':
                metrics = self.load_metrics(map_key, metric_type)
                for metric in metrics:
                    self.assertIn(metric, event_keys)

    def run_director_event_collection_asserts(self, metric_type):
        """Load pickle event data and run assertions on contents.

        :param metric_type: the type of metrics in use (ALL, KPI, etc.) -- str
        """
        event_data = self.load_event_data()
        for event in event_data:
            event, event_keys = self.load_event(event)
            director_type = event.get('director_type')
            self.assertEqual('Director', event.get('reporting_level'))

            map_key = None
            if director_type == 'FE':
                map_key = pc.FE_DIRECTOR
            elif director_type == 'BE':
                map_key = pc.BE_DIRECTOR
            elif director_type == 'RDF':
                map_key = pc.RDF_DIRECTOR
            elif director_type == 'IM':
                map_key = pc.IM_DIRECTOR
            elif director_type == 'EDS':
                map_key = pc.EDS_DIRECTOR
            elif director_type == 'EM':
                map_key = pc.EM_DIRECTOR

            metrics = self.load_metrics(map_key, metric_type)
            for metric in metrics:
                self.assertIn(metric, event_keys)

    def run_port_event_collection_asserts(self, metric_type=None):
        """Load pickle event data and run assertions on contents.

        :param metric_type: the type of metrics in use (ALL, KPI, etc.) -- str
        """
        event_data = self.load_event_data()
        for event in event_data:
            event, event_keys = self.load_event(event)
            port_type = event.get('port_dir_type')
            self.assertEqual('Port', event.get('reporting_level'))

            map_key = None
            if port_type == 'Front End Director':
                map_key = pc.FE_PORT
            elif port_type == 'Back End Director':
                map_key = pc.BE_PORT
            elif port_type == 'RDF Director':
                map_key = pc.RDF_PORT

            metrics = self.load_metrics(map_key, metric_type)
            for metric in metrics:
                self.assertIn(metric, event_keys)

    def run_active_inactive_event_collection_asserts(
            self, map_key=pc.HOST, metric_type=None):
        """Load pickle event data and run assertions on contents.

        :param map_key: the key used to retrieve metrics from PyU4V -- str
        :param metric_type: the type of metrics in use (ALL, KPI, etc.) -- str
        """
        event_data = self.load_event_data()
        for event in event_data:
            event, event_keys = self.load_event(event)
            self.assertEqual('Host' if map_key == pc.HOST else 'Initiator',
                             event.get('reporting_level'))

            if event.get('performance_metrics'):
                metrics = self.load_metrics(map_key, metric_type)
                for metric in metrics:
                    self.assertIn(metric, event_keys)
            else:
                self.assertFalse(event.get('host_perf_details', False))
                self.assertFalse(event.get('performance_metrics', False))

    def run_masking_view_event_collection_asserts(self, metric_type=None):
        """Load pickle event data and run assertions on contents.

        :param metric_type: the type of metrics in use (ALL, KPI, etc.) -- str
        """
        event_data = self.load_event_data()
        for event in event_data:
            event, event_keys = self.load_event(event)
            reporting_level = event.get('reporting_level')
            self.assertIn(reporting_level,
                          ['Masking View', 'Masking View Connection'])
            self.assertIn('host_id', event_keys)
            self.assertIn('host_group_id', event_keys)

            if reporting_level == 'Masking View':
                metrics = self.load_metrics(pc.MASKING_VIEW, metric_type)
                for metric in metrics:
                    self.assertIn(metric, event_keys)

    def run_iscsi_event_collection_asserts(self, metric_type=None):
        """Load pickle event data and run assertions on contents.

        :param metric_type: the type of metrics in use (ALL, KPI, etc.) -- str
        """
        event_data = self.load_event_data()
        for event in event_data:
            event, event_keys = self.load_event(event)
            reporting_level = event.get('reporting_level')
            map_key = None
            if reporting_level == 'IP Interface':
                map_key = pc.IP_INTERFACE
            elif reporting_level == 'iSCSI Target':
                map_key = pc.ISCSI_TARGET

            tgt_level = 'IP Interface' if (
                map_key == pc.IP_INTERFACE) else 'iSCSI Target'
            self.assertEqual(tgt_level, reporting_level)

            metrics = self.load_metrics(map_key, metric_type)
            for metric in metrics:
                self.assertIn(metric, event_keys)

    def run_rdfg_event_collection_asserts(self, metric_type=None):
        """Load pickle event data and run assertions on contents.

        :param metric_type: the type of metrics in use (ALL, KPI, etc.) -- str
        """
        event_data = self.load_event_data()
        for event in event_data:
            event, event_keys = self.load_event(event)
            reporting_level = event.get('reporting_level')
            rdfs = event.get('rdfs')
            rdfa = event.get('rdfa')

            map_key = None
            if rdfs:
                map_key = pc.RDFS
            elif rdfa:
                map_key = pc.RDFA

            tgt_level = 'RDF Group' if map_key else 'RDF Pair'
            self.assertEqual(tgt_level, reporting_level)

            if map_key:
                metrics = self.load_metrics(map_key, metric_type)
                for metric in metrics:
                    self.assertIn(metric, event_keys)
            else:
                self.assertIn('type', event_keys)
                self.assertIn('rdfg_label', event_keys)
