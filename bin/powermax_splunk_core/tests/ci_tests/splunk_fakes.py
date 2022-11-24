"""bin/powermax_splunk_core/tests/ci_tests/splunk_fakes.py"""

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

import configparser
import pickle

from pathlib import Path

CWD = Path(__file__).parent
CONFIG_PATH = 'ci_config.ini'
PICKLE_PATH = 'ci_pickle.p'


class FakeSplunkHelper(object):
    """Fake Splunk Helper."""

    def __init__(self):
        self.log_level = 'TEST'
        self.arg_mapping = self.load_environment_configuration()

    @staticmethod
    def _bool_check(_input):
        """Check if an input is true/false.

        :param _input: text input -- str
        :returns: bool
        """
        return bool(_input in [True, 'True', 'true', 1])

    def load_environment_configuration(self):
        """Load Splunk CI environment configuration."""
        config_file_path = Path.joinpath(CWD, CONFIG_PATH)
        config = configparser.ConfigParser()
        config.read(config_file_path)
        try:
            assert 'environment_config' in config
            c = config['environment_config']
        except AssertionError as e:
            print('CI config file is missing [environment_config] stanza.')
            raise AssertionError from e

        arg_mapping = {
            'u4v_ip_address': c['u4v_ip_address'],
            'u4v_port': c['u4v_port'],
            'u4v_username': c['u4v_username'],
            'u4v_password': c['u4v_password'],
            'u4v_vmax_id': c['u4v_vmax_id'],
            'rest_request_timeout': c['rest_request_timeout'],
            'enable_ssl': self._bool_check(c['enable_ssl']),
            'ssl_cert_location': c['ssl_cert_location'],
            'interval': c['interval'],
            'select_array': self._bool_check(c['select_array']),
            'select_srp': self._bool_check(c['select_srp']),
            'select_sg': self._bool_check(c['select_sg']),
            'select_director': self._bool_check(c['select_director']),
            'select_port': self._bool_check(c['select_port']),
            'select_pg': self._bool_check(c['select_pg']),
            'select_iscsi': self._bool_check(c['select_iscsi']),
            'select_host': self._bool_check(c['select_host']),
            'select_mv': self._bool_check(c['select_mv']),
            'select_initiator': self._bool_check(c['select_initiator']),
            'select_rdf': self._bool_check(c['select_rdf']),
            'select_metro_dr': self._bool_check(c['select_metro_dr']),
            'select_snap_policy': self._bool_check(c['select_snap_policy']),
            'select_alerts': self._bool_check(c['select_alerts']),
            'select_audit_logs': self._bool_check(c['select_audit_logs']),
            'select_array_metrics': c['select_array_metrics'],
            'select_srp_metrics': c['select_srp_metrics'],
            'select_sg_metrics': c['select_sg_metrics'],
            'select_fe_dir_metrics': c['select_fe_dir_metrics'],
            'select_be_dir_metrics': c['select_be_dir_metrics'],
            'select_rdf_dir_metrics': c['select_rdf_dir_metrics'],
            'select_im_dir_metrics': c['select_im_dir_metrics'],
            'select_eds_dir_metrics': c['select_eds_dir_metrics'],
            'select_em_dir_metrics': c['select_em_dir_metrics'],
            'select_fe_port_metrics': c['select_fe_port_metrics'],
            'select_be_port_metrics': c['select_be_port_metrics'],
            'select_rdf_port_metrics': c['select_rdf_port_metrics'],
            'select_pg_metrics': c['select_pg_metrics'],
            'select_iscsi_target_metrics': c['select_iscsi_target_metrics'],
            'select_ip_interface_metrics': c['select_ip_interface_metrics'],
            'select_host_metrics': c['select_host_metrics'],
            'select_initiator_metrics': c['select_initiator_metrics'],
            'select_mv_metrics': c['select_mv_metrics'],
            'select_rdfs_metrics': c['select_rdfs_metrics'],
            'select_rdfa_metrics': c['select_rdfa_metrics']}

        return arg_mapping

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
        return 'ci_sourcetype'

    @staticmethod
    def get_output_index():
        """Get Splunk output index.

        :returns: output index -- str
        """
        return 'ci_index'

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
    def write_event(data):
        """Write event to pickle file.

        :param data:
        :returns:
        """
        assert type(data) is dict

        file_path = Path.joinpath(CWD, PICKLE_PATH)
        if file_path.exists():
            with open(file_path, 'rb') as open_file:
                events = pickle.load(open_file)
                assert type(events) is list
                assert events
                events.append(data)
        else:
            events = [data]

        with open(file_path, 'wb') as out_file:
            pickle.dump(events, out_file)

        assert file_path.exists()

    @staticmethod
    def load_event_data():
        """Load pickle event data.

        :raises:
        :returns:
        """
        file_path = Path.joinpath(CWD, PICKLE_PATH)
        if file_path.exists():
            try:
                with open(file_path, 'rb') as open_file:
                    events = pickle.load(open_file)
                    assert type(events) is list
            except OSError as e:
                raise OSError(
                    'There was a problem loading pickle data.') from e
        else:
            raise EnvironmentError('No pickle event data found.')

        return events

    @staticmethod
    def cleanup_event_data():
        """Cleanup event pickle data."""
        file_path = Path.joinpath(CWD, PICKLE_PATH)
        file_path.unlink(missing_ok=True)
