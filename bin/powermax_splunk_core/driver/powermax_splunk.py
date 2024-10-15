"""bin/powermax_splunk_core/driver/powermax_splunk.py"""
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
import math
import re

import PyU4V
from PyU4V.utils import exception

from .utils import powermax_constants as pc
from .utils import powermax_key_consistency

consistent_keys = powermax_key_consistency.consistent_keys


class PMaxSplunk:
    """PowerMax for Splunk common functions."""

    def __init__(self, helper, event_writer):
        self.helper = helper
        self.ew = event_writer
        self.source_type = None
        self.index = helper.get_output_index()
        self.timestamp = None
        self.interval = None
        self.source = None

        self.conn = self._establish_pyu4v_connection()
        self.array_id = self.conn.array_id
        self.name = self.helper.get_arg('name')
        self.perf = self.conn.performance

        self.enabled_categories = dict()
        self.enabled_metrics = dict()
        self._set_env_configuration_settings()
        self._set_enabled_categories()
        self._set_enabled_metrics()
        self._validate_configuration()

    def _establish_pyu4v_connection(self):
        """Establish connection with Unisphere REST API.

        :returns: PyU4V Unisphere REST connection -- obj
        """
        ip_address = self.helper.get_arg('u4v_ip_address')
        port = self.helper.get_arg('u4v_port')
        username = self.helper.get_arg('u4v_username')
        password = self.helper.get_arg('u4v_password')
        array_id = self.helper.get_arg('u4v_vmax_id')
        rest_timeout = float(self.helper.get_arg('rest_request_timeout'))

        # SSL Setting
        ssl_verify = True

        # Initialise connection and set timeout value
        conn = PyU4V.U4VConn(
            username=username, password=password, server_ip=ip_address,
            port=port, verify=ssl_verify, array_id=array_id,
            application_type='Splunk-{}'.format(pc.VERSION))
        conn.rest_client.timeout = rest_timeout

        return conn

    def _set_env_configuration_settings(self):
        """Set PowerMax for Splunk enabled categories"""
        # Set the log level
        log_level = self.helper.get_log_level()
        self.helper.set_log_level(log_level)
        # Set the metrics collection interval
        self.interval = int(self.helper.get_arg('interval'))
        # Set the PowerMax TA source type
        self.source_type = self.helper.get_sourcetype()
        # Set the PowerMax TA target Splunk Index
        self.index = self.helper.get_output_index()
        # Define the PowerMax TA input source
        self.source = 'vmax://{ip}::{id}'.format(
            ip=self.helper.get_arg('u4v_ip_address'),
            id=self.array_id)

    def _set_enabled_categories(self):
        """Set enabled performance categories for data input."""
        # Set the PowerMax TA enabled categories
        levels = pc.REPORTING_LEVELS
        # For each reporting level in categories
        for rl_key in levels:
            input_key = pc.REPORTING_LEVELS_KEY_MAP.get(rl_key)
            is_enabled = self._is_category_enabled(input_key)
            self.enabled_categories[rl_key] = is_enabled
            self.log_debug('Performance category {c} enabled: {e}'.format(
                c=rl_key, e=is_enabled))

    def _is_category_enabled(self, input_key):
        """Load a PowerMax for Splunk performance category is_enabled status.

        :param input_key: data input category enabled key setting -- str
        :returns: is category enabled -- bool
        """
        is_enabled = False
        # PowerMax for Splunk v2.x and earlier environments may still use
        # True/False for turning on/off reporting categories. If this scenario
        # is met, follow old add-on precedent and return all performance
        # metrics. Onus on the user to move PowerMax settings in input.conf
        # to v3.x standards.
        if isinstance(self.helper.get_arg(input_key), bool):
            if self.helper.get_arg(input_key):
                is_enabled = True
        # If the category settings does not match '*_off' it is enabled
        elif not re.search(r'^[a-z_]*off$', self.helper.get_arg(input_key)):
            is_enabled = True

        return is_enabled

    def _set_enabled_metrics(self):
        """Set enabled metrics for performance category."""
        # Set the PowerMax TA enabled metrics
        perf_categories = pc.PERFORMANCE_CATEGORIES
        perf_map = pc.PERFORMANCE_KEY_MAP
        for pc_key in perf_categories:
            # Dont set anything for BEPort, EDSDirector and IMDirector for V4, not valid
            if self.conn.performance.is_v4:
                if pc_key in [pc.BE_PORT, pc.IM_DIRECTOR,
                              pc.EDS_DIRECTOR]:
                    self.log_debug(msg=(
                        'Category {c} not supported in V4, removing from list '
                        'of enabled category targets.'.format(c=pc_key)))
                    continue
            # Dont set anything for EMDirector for V3, not valid
            else:
                if pc_key in [pc.EM_DIRECTOR]:
                    self.log_debug(msg=(
                        'Category {c} not supported in V3, removing from list '
                        'of enabled category targets.'.format(c=pc_key)))
                    continue

            metrics = list()
            perf_cat = perf_map.get(pc_key)
            input_key = perf_cat.get(pc.INPUT_KEY)
            input_setting = self.helper.get_arg(input_key)

            if self._is_category_enabled(input_key):
                # If legacy format with True setting use ALL metrics
                if isinstance(input_setting, bool):
                    metrics = 'ALL'
                elif input_setting == perf_cat[pc.ALL]:
                    metrics = 'ALL'
                elif input_setting == perf_cat[pc.KPI]:
                    metrics = 'KPI'
                elif input_setting == perf_cat[pc.CUSTOM]:
                    metrics = self._load_custom_metrics(pc_key, perf_cat)

                self.log_debug('{p} metric configuration setting: {m}'.format(
                    p=pc_key, m=metrics))

            self.enabled_metrics[pc_key] = metrics

    def _load_custom_metrics(self, reporting_level, perf_cat):
        """Load user custom metrics list and validate.

        Note: If a user specifies custom metrics but none of the metrics
        are valid the value then set for metrics is 'KPI'. This is due to user
        changing from default 'OFF' value indicating intention to report on
        a given reporting category. In this case it is better to return some
        metrics and notify the user with WARNING and ERROR messages indicating
        a problem.

        :param reporting_level: the Unisphere performance category -- str
        :param perf_cat: the performance category to load metrics for -- str
        :returns: validated performance metrics -- list
        """
        # Get reporting level custom metrics list
        metrics_key = perf_cat[pc.METRICS]
        custom_metrics = self.helper.get_arg(metrics_key)
        if custom_metrics:
            # Split comma separated string into list, strip white space
            custom_metrics = [x.strip() for x in custom_metrics.split(',')]
            # Get the full list of performance metrics
            full_metric_list = self.perf.get_performance_metrics_list(
                category=perf_cat[pc.U4P_CAT])
            # Verify we have custom metrics set and all metrics are valid, if
            # not remove the metric from the custom list and warn user
            if custom_metrics and not (
                    all(m in set(full_metric_list) for m in custom_metrics)):
                for metric in custom_metrics:
                    if metric not in set(full_metric_list):
                        self.log_warning(
                            '{r} metric {m} from custom metric list is not '
                            'valid, removing from targeted level '
                            'metrics.'.format(
                                r=reporting_level, m=metric))
                        custom_metrics.remove(metric)

        # If there are no custom metrics left or user has not set list
        # correctly in inputs.conf set the metrics list to KPI only
        if not custom_metrics:
            self.log_error(
                'There have been no valid performance metrics specified for '
                'reporting level {r}. Defaulting to KPI metrics only.'.format(
                    r=reporting_level))
            return 'KPI'
        else:
            return custom_metrics

    def _validate_configuration(self):
        """Run array and input param validation checks.

        There is a facility to run validation checks from input_module_inputs
        but it is too restrictive, it is better run here so detailed
        environment checks can be run against Unisphere REST API.

        :raises: ValueError, EnvironmentError
        """
        self.log_info('Starting environment validations checks.')
        # 1. Check that the interval is divisible by 300 and no lower than 300
        if self.interval % 300 != 0 or self.interval < 300:
            self.log_critical('Interval must be divisible by 300.',
                              raise_exception=True, exc=ValueError)
        else:
            self.log_info('Passed collection interval check.')

        # 2. Check if Unisphere is responding & is required min version
        __, major_version = self.conn.common.get_uni_version()
        self.log_info(major_version)
        if int(major_version) < 100:
            msg = ('Unisphere is not required version, please upgrade '
                   'Unisphere to required version. '
                   'Please see '
                   'https://powermax-for-splunk.readthedocs.io/en/latest/'
                   'Exiting metrics collection run')
            self.log_critical(msg, raise_exception=True, exc=EnvironmentError)
        else:
            self.log_info('Passed Unisphere version check.')

        # 3. Check if array is V3 model or newer
        env_v3_list = self.conn.common.get_v3_or_newer_array_list()
        if self.array_id not in set(env_v3_list):
            msg = ('Array not found on specified Unisphere instance. Please '
                   'check array ID in data input configuration. Exiting '
                   'metrics collection run.')
            self.log_critical(msg, raise_exception=True, exc=EnvironmentError)
        else:
            self.log_info('Passed array model check.')

        # 4. Check is array local & performance registered
        if not self.perf.is_array_diagnostic_performance_registered():
            msg = ('Array not performance registered or is not local to '
                   'Unisphere. Exiting metrics collection run.')
            self.log_critical(msg, raise_exception=True, exc=EnvironmentError)
        else:
            self.log_info('Passed performance registration check.')

        # 5. If performance registered, is timestamp up to date
        timestamp = int(self.perf.get_last_available_timestamp())
        is_recent = self.perf.is_timestamp_current(
            timestamp, self.interval / 60)
        if not is_recent:
            msg = ('Array performance timestamp {t} not current. Exiting '
                   'metrics collection run.'.format(t=timestamp))
            self.log_critical(msg, raise_exception=True, exc=EnvironmentError)
        else:
            self.timestamp = timestamp
            self.log_info(
                'Passed performance timestamp recency check: {t}.'.format(
                    t=self.timestamp))

    def _merge_dicts(self, *dict_args, timestamp=None):
        """Merge one or more dictionaries together.

        This function will convert camel-case to snake-case and make
        adjustments for spelling errors to ensure consistent keys with previous
        releases.

        :param dict_args: data for merging -- dicts
        :returns: merged data -- JSON
        """
        result = dict()
        # For each dict passed in
        for dictionary in dict_args:
            # Check the dict is populated
            if dictionary is not None:
                # Write the results to the new dict, at the same time convert
                # mixed case standards to snake case standard
                for k, v in dictionary.items():
                    # We can ignore duplicate redundant keys
                    if k not in {'arrayId', 'symmetrixId', 'symmId', 'array',
                                 'timestamp'}:
                        new_key = self.conn.common.convert_to_snake_case(k)
                        if consistent_keys.get(new_key):
                            new_key = consistent_keys.get(new_key)
                        result[new_key] = v

        result['timestamp'] = timestamp if timestamp else self.timestamp
        result['array_id'] = self.array_id

        return json.dumps(result)

    def _flatten_dict(self, src_dict):
        """Recursively flatten dictionary.

        This is required from Unisphere 10.x and newer because responses can
        now contain up to four layers deep of nested dictionaries. Iteratively
        cycling through these was no longer feasible

        :param src_dict: source data -- dict
        :returns: exploded data -- dict
        """
        def items():
            if isinstance(src_dict, dict):
                for k, v in src_dict.items():
                    if isinstance(v, dict):
                        for sk, sv in self._flatten_dict(v).items():
                            yield k + '_' + sk, sv
                    elif isinstance(v, list):
                        for x in v:
                            if isinstance(x, dict):
                                for sk, sv in self._flatten_dict(v).items():
                                    yield k + '_' + sk, sv
                    else:
                        yield k, v
            elif isinstance(src_dict, list):
                info = src_dict[0]
                for k, v in info.items():
                    yield k, v

        return dict(items())

    def _extract_array_alert_summary(self, summary):
        """Extract array alert summary from PyU4V response.

        :param summary: source alert data -- dict
        :returns: exploded alert data -- dict
        """
        response = dict()
        found_symm = False
        if summary:
            for symm in summary.get('symmAlertSummary'):
                if symm.get('symmId') == self.array_id:
                    found_symm = True
                    perf_alerts = symm.get('performanceAlertSummary')
                    for k, v in perf_alerts.items():
                        response['array_performance_alert_{k}'.format(k=k)] = v
                    array_alerts = symm.get('arrayAlertSummary')
                    for k, v in array_alerts.items():
                        response['array_alert_{k}'.format(k=k)] = v

            if not found_symm:
                response['array_alert_details'] = False
                response['array_alert_message'] = (
                    'No Array alerts summary data available')

        return response

    @staticmethod
    def _process_performance_response(performance_data):
        """Extract raw performance data and merge with outer response dict.

        :param performance_data: Unisphere performance response -- dict
        :returns: updated performance results -- dict
        """
        if performance_data.get('result'):
            raw_data = performance_data.get('result')[0].copy()
            performance_data.update(raw_data)
            performance_data.pop('result')
            performance_data.pop('reporting_level')
        return performance_data

    def write_event(self, data):
        """Write a PowerMax event to the Splunk index.

        :param data: data for writing -- JSON
        """
        self.ew.write_event(self.helper.new_event(
            source=self.source, index=self.index, sourcetype=self.source_type,
            data=data))

    def log_debug(self, msg):
        """Log formatted debug message.

        :param msg: message -- str
        """
        self.helper.log_debug(
            'Input: {i} | Array: {a} | {m}'.format(
                i=self.name, a=self.array_id, m=msg))

    def log_info(self, msg):
        """Log formatted info message.

        :param msg: message -- str
        """
        self.helper.log_info(
            'Input: {i} | Array: {a} | {m}'.format(
                i=self.name, a=self.array_id, m=msg))

    def log_warning(self, msg):
        """Log formatted warning message.

        :param msg: message -- str
        """
        self.helper.log_warning(
            'Input: {i} | Array: {a} | {m}'.format(
                i=self.name, a=self.array_id, m=msg))

    def log_critical(self, msg, raise_exception=False, exc=None):
        """Log formatted critical message.

        :param msg: message -- str
        :param raise_exception: if exception should be raised -- bool
        :param exc: exception to raise -- exception
        :raises Exception
        """
        log_msg = 'Input: {i} | Array: {a} | {m}'.format(
            i=self.name, a=self.array_id, m=msg)
        self.helper.log_critical(log_msg)
        if raise_exception:
            raise exc(log_msg)

    def log_error(self, msg, raise_exception=False, exc=None):
        """Log formatted error message.

        :param msg: message -- str
        :param raise_exception: if exception should be raised -- bool
        :param exc: exception to raise -- exception
        :raises Exception
        """
        log_msg = 'Input: {i} | Array: {a} | {m}'.format(
            i=self.name, a=self.array_id, m=msg)
        self.helper.log_error(log_msg)
        if raise_exception:
            raise exc(log_msg)

    def log_collection_error(self, asset_type, asset_id=None):
        """Log an error when an issue has been encountered during collection.

        :param asset_type: failed asset type -- str
        :param asset_id: failed asset ID -- str
        """
        prefix = ''
        if asset_id:
            prefix = '{a}: {a_id} | '.format(a=asset_type, a_id=asset_id)

        msg = prefix + (
            'There was an issue collecting {at} metrics, please check status '
            'code for further information. This may be a temporary Unisphere '
            'response error which will clear itself.'.format(at=asset_type))
        self.log_error(msg)

    def process_collection_duration(self, start_time, end_time):
        """Determine if the interval is suitable for collection run duration.

        :param start_time: start time in seconds since epoch -- int
        :param end_time: end time in seconds since epoch -- int
        """
        run_time = end_time - start_time
        # 300 here is the lowest granularity available in seconds by
        # Unisphere, intervals are calculated in increments of 300
        suggested_interval = int(math.ceil(run_time / 300)) * 300

        if suggested_interval == 0:
            suggested_interval = 300

        if suggested_interval > self.interval:
            self.log_critical(
                'Interval of {i} has been set in input configuration but run '
                'required {r} seconds to complete. This has a negative impact '
                'on PowerMax for Splunk performance. Please refine enabled '
                'performance categories to meet interval or increase interval '
                'to {s} seconds.'.format(
                    i=self.interval, r=int(run_time), s=suggested_interval))
        else:
            self.log_info(
                'Completed metrics collection run in {r} seconds.'.format(
                    r=int(run_time)))

    def get_array_details(self):
        """Get array level information from PyU4V.

        Get all array level details for the following reporting levels:
        summary, system, WLP, migration, replication details, replication
        capabilities, alert summary, performance details.

        :returns: array summary -- JSON
        """
        self.log_debug('Collecting array data.')
        # 1. Get array SLO provisioning info
        array_slo_pro = self._flatten_dict(
            self.conn.provisioning.get_array())
        if not array_slo_pro:
            array_slo_pro = {
                'array_summary_details': False,
                'array_summary_message': 'No Array summary data available'}
        array_slo_pro['reporting_level'] = 'Array'

        # 2. Get array System info
        array_system = self._flatten_dict(
            self.conn.common.get_array(self.array_id))
        if not array_system:
            array_system = {
                'array_system_details': False,
                'array_system_message': 'No Array system data available'}

        # 3. Get array WLP info
        array_wlp = self.conn.wlp.get_capabilities(self.array_id)
        if array_wlp:
            array_wlp = array_wlp[0]
        else:
            array_wlp = {
                'array_wlp_details': False,
                'array_wlp_message': 'No Array WLP data available'}

        # 4. Get array migration info
        array_migration_info = self.conn.migration.get_migration_info()
        if not array_migration_info:
            array_migration_info = {
                'array_migration_details': False,
                'array_migration_message': 'No Array migration data available'}

        array_migration_cap = (
            self.conn.migration.get_array_migration_capabilities())
        if not array_migration_cap:
            array_migration_cap = {
                'array_migration_capabilities_detail': False,
                'array_migration_capabilities_message':
                    'No Array migration capability data available'}

        # 5. Get array replication details
        array_rep_cap = (
            self.conn.replication.get_array_replication_capabilities())
        if not array_rep_cap:
            array_rep_cap = {
                'array_replication_capability_details': False,
                'array_replication_capability_message':
                    'No Array replication data available'}

        # 6. Get array health details
        array_system_health = self.conn.system.get_system_health()
        array_health_stats = dict()
        if array_system_health:
            for hsm in array_system_health.get('health_score_metric'):
                key = 'health_{h}'.format(
                    h=self.conn.common.convert_to_snake_case(
                        hsm.get('metric')))
                value = hsm.get('health_score')
                array_health_stats[key] = value
        else:
            array_health_stats = {
                'array_health_details': False,
                'array_health_message': 'No Array health data available'}

        # Get Array Alert summary
        array_alerts = self._extract_array_alert_summary(
            self.conn.system.get_alert_summary())
        if not array_alerts:
            array_alerts = {
                'array_alert_details': False,
                'array_alert_message': 'No Array alert data available'}

        # Get Array performance details
        metrics = self.enabled_metrics.get(pc.ARRAY)
        array_performance = self.perf.get_array_stats(
            metrics=metrics, start_time=str(self.timestamp),
            end_time=str(self.timestamp))
        if not array_performance:
            msg = 'No Array performance data available.'
            self.log_warning(msg)
            array_performance = {
                'array_perf_details': False, 'array_perf_message': msg}
        else:
            array_performance = self._process_performance_response(
                array_performance)

        return self._merge_dicts(
            array_slo_pro, array_system, array_wlp, array_migration_info,
            array_migration_cap, array_rep_cap, array_alerts,
            array_health_stats, array_performance)

    def get_srp_details(self, srp_id):
        """Get all SRP details for a given SRP.

        :param srp_id: SRP ID -- str
        :returns: SRP details -- JSON
        """
        self.log_debug(
            'SRP: {s} | Collecting SRP data.'.format(s=srp_id))
        # Get SRP details
        srp_details = self._flatten_dict(
            self.conn.provisioning.get_srp(srp=srp_id))
        srp_details['reporting_level'] = 'SRP'

        return self._merge_dicts(srp_details)

    def get_srp_performance_info(self, srp_id):
        """Get all SRP details for a given SRP.

        We can no longer rely on SRP ID from sloprovisioning endpoints,
        performance endpoints required SRP ID and emulation (FBA/CKD) for V4.

        :param srp_id: SRP ID -- str
        :returns: SRP performance details -- JSON
        """
        # Get SRP performance metrics
        metrics = self.enabled_metrics.get(pc.SRP)

        srp_info = dict()
        srp_info['reporting_level'] = 'SRP_PERFORMANCE'
        srp_info['srp_performance_id'] = srp_id
        srp_info['srp_src_id'] = srp_id.split(' ')[0]

        srp_performance = self.perf.get_storage_resource_pool_stats(
            metrics=metrics, srp_id=srp_id,
            start_time=self.timestamp, end_time=self.timestamp)
        srp_performance = self._process_performance_response(srp_performance)
        if not srp_performance:
            msg = 'No SRP performance data available.'
            self.log_warning('SRP: {s} | {m}'.format(s=srp_id, m=msg))
            srp_performance = {
                'srp_perf_details': False, 'srp_perf_message': msg}

        return self._merge_dicts(srp_info, srp_performance)

    def get_storage_group_details(self, storage_group_id):
        """Get all Storage Group details for a given Storage Group.

        :param storage_group_id: storage group id -- str
        :returns: storage group details -- JSON
        """
        self.log_debug(
            'SG: {s} | Collecting Storage Group data.'.format(
                s=storage_group_id))
        # Get SG details
        sg_details = self.conn.provisioning.get_storage_group(storage_group_id)
        sg_details = self._flatten_dict(sg_details)
        sg_details['service_level'] = sg_details.get('service_level', 'NONE')
        sg_details['workload'] = sg_details.get('workload', 'NONE')
        sg_details['srp'] = sg_details.get('srp', 'NONE')
        sg_details['reporting_level'] = 'SG'

        # Get SG performance details
        metrics = self.enabled_metrics.get(pc.STORAGE_GROUP)
        sg_performance = self.perf.get_storage_group_stats(
            metrics=metrics, storage_group_id=storage_group_id,
            start_time=self.timestamp, end_time=self.timestamp)

        if not sg_performance:
            msg = 'No SG performance data available.'
            self.log_warning(
                'SG: {s} | {m}'.format(s=storage_group_id, m=msg))
            sg_performance = {
                'sg_perf_details': False, 'sg_perf_message': msg}
        else:
            sg_performance = self._process_performance_response(
                sg_performance)

        return self._merge_dicts(sg_details, sg_performance)

    def get_director_details(self, director_id):
        """Get director details for a given director.

        :param director_id: director ID -- str
        :returns: director details -- JSON
        """
        self.log_debug(
            'Director: {d} | Collecting Director data.'.format(d=director_id))
        dir_details = self.conn.system.get_director(director=director_id)
        dir_details['reporting_level'] = 'Director'
        if dir_details.get('srdf_groups'):
            dir_details['num_srdf_groups'] = len(dir_details['srdf_groups'])
            dir_details.pop('srdf_groups')

        perf_f, metrics, dir_performance = None, None, None

        if any(x in director_id for x in ['DF', 'DX']):
            perf_f = self.perf.get_backend_director_stats
            metrics = self.enabled_metrics.get(pc.BE_DIRECTOR)
            dir_details['director_type'] = 'BE'
        elif any(x in director_id for x in ['EF', 'FA', 'FE', 'SE', 'OR']):
            perf_f = self.perf.get_frontend_director_stats
            metrics = self.enabled_metrics.get(pc.FE_DIRECTOR)
            dir_details['director_type'] = 'FE'
        elif any(x in director_id for x in ['RF', 'RE']):
            perf_f = self.perf.get_rdf_director_stats
            metrics = self.enabled_metrics.get(pc.RDF_DIRECTOR)
            dir_details['director_type'] = 'RDF'
        elif 'IM' in director_id:
            perf_f = self.perf.get_im_director_stats
            metrics = self.enabled_metrics.get(pc.IM_DIRECTOR)
            dir_details['director_type'] = 'IM'
        elif 'ED' in director_id:
            perf_f = self.perf.get_eds_director_stats
            metrics = self.enabled_metrics.get(pc.EDS_DIRECTOR)
            dir_details['director_type'] = 'EDS'
        elif any(x in director_id for x in ['EM']):
            perf_f = self.perf.get_em_director_stats
            metrics = self.enabled_metrics.get(pc.EM_DIRECTOR)
            dir_details['director_type'] = 'EM'
        else:
            msg = (
                'Director: {d} | Not able to determine director type'.format(
                    d=director_id))
            self.log_error(msg, raise_exception=True,
                           exc=exception.VolumeBackendAPIException)

        if perf_f:
            dir_performance = perf_f(
                metrics=metrics, director_id=director_id,
                start_time=self.timestamp, end_time=self.timestamp)

        if not dir_performance:
            msg = 'No Director performance data available.'
            self.log_warning(
                'Director: {d} | {m}'.format(d=director_id, m=msg))
            dir_performance = {
                'dir_perf_details': False, 'dir_perf_message': msg}
        else:
            dir_performance = self._process_performance_response(
                dir_performance)

        return self._merge_dicts(dir_details, dir_performance)

    def get_director_or_rdf_details(self, director_id):
        """Get OR director RDF details for a given director.

        :param director_id: director ID -- str
        :returns: director details -- JSON
        """
        self.log_debug(
            'OR Director: {d} | Collecting RDF Director data.'.format(d=director_id))
        dir_details = self.conn.system.get_director(director=director_id)
        dir_details['reporting_level'] = 'Director'
        if dir_details.get('srdf_groups'):
            dir_details['num_srdf_groups'] = len(dir_details['srdf_groups'])
            dir_details.pop('srdf_groups')

        perf_f, metrics, dir_performance = None, None, None

        if any(x in director_id for x in ['OR']):
            perf_f = self.perf.get_rdf_director_stats
            metrics = self.enabled_metrics.get(pc.RDF_DIRECTOR)
            dir_details['director_type'] = 'RDF'
        else:
            msg = (
                'Director: {d} | Not able to determine director type'.format(
                    d=director_id))
            self.log_error(msg, raise_exception=True,
                           exc=exception.VolumeBackendAPIException)

        if perf_f:
            dir_performance = perf_f(
                metrics=metrics, director_id=director_id,
                start_time=self.timestamp, end_time=self.timestamp)

        if not dir_performance:
            msg = 'No OR Director RDF performance data available.'
            self.log_warning(
                'Director: {d} | {m}'.format(d=director_id, m=msg))
            dir_performance = {
                'dir_perf_details': False, 'dir_perf_message': msg}
        else:
            dir_performance = self._process_performance_response(
                dir_performance)

        return self._merge_dicts(dir_details, dir_performance)

    def get_port_details(self, port_key):
        """Get Port details for a given Port.

        :param port_key: director id & port id -- tuple(str, str)
        :returns: port details -- JSON
        """
        director_id = port_key['directorId']
        port_id = port_key['portId']
        self.log_debug(
            'Port: {d}:{p} | Collecting Port data.'.format(
                d=director_id, p=port_id))

        port_details = self.conn.system.get_director_port(
            director=director_id, port_no=port_id)
        port_details = port_details.get('symmetrixPort')
        port_details['reporting_level'] = 'Port'
        port_details['port_id'] = port_id
        port_details['director_id'] = director_id
        port_details['dir_port_key'] = '{d}:{p}'.format(
            d=director_id, p=port_id)
        port_details.pop('symmetrixPortKey')

        perf_f, metrics, port_performance = None, None, None
        if any(x in director_id for x in ['DF', 'DX']):
            perf_f = self.perf.get_backend_port_stats
            metrics = self.enabled_metrics.get(pc.BE_PORT)
            port_details['port_dir_type'] = 'Back End Director'
        elif any(x in director_id for x in ['EF', 'FA', 'FE', 'SE', 'OR']):
            perf_f = self.perf.get_frontend_port_stats
            metrics = self.enabled_metrics.get(pc.FE_PORT)
            port_details['port_dir_type'] = 'Front End Director'
        elif any(x in director_id for x in ['RF', 'RE', 'OR']):
            perf_f = self.perf.get_rdf_port_stats
            metrics = self.enabled_metrics.get(pc.RDF_PORT)
            port_details['port_dir_type'] = 'RDF Director'
        else:
            msg = 'Port: {d}:{p} | Not able to determine port type'.format(
                d=director_id, p=port_id)
            self.log_error(msg, raise_exception=True,
                           exc=exception.VolumeBackendAPIException)

        if perf_f:
            port_performance = perf_f(
                metrics=metrics, director_id=director_id, port_id=port_id,
                start_time=self.timestamp, end_time=self.timestamp)

        if not port_performance:
            msg = 'No Port performance data available.'
            self.log_warning(
                'Port: {d}:{p} | {m}'.format(d=director_id, p=port_id, m=msg))
            port_performance = {
                'port_perf_details': False, 'port_perf_message': msg}
        else:
            port_performance = self._process_performance_response(
                port_performance)

        return self._merge_dicts(port_details, port_performance)

    def get_port_group_details(self, port_group_id):
        """Get Port Group details for a given Port Group.

        :param port_group_id: port group ID -- str
        :returns: port group details -- dict
        """
        self.log_debug(
            'Port Group: {p} | Collecting Port Group data.'.format(
                p=port_group_id))

        port_group_details = self.conn.provisioning.get_port_group(
            port_group_id)
        port_group_details['reporting_level'] = 'Port Group'
        if port_group_details.get('symmetrixPortKey'):
            port_list = list()
            for dir_port in port_group_details.get('symmetrixPortKey'):
                port_list.append('{d}:{p}'.format(
                    d=dir_port.get('directorId'), p=dir_port.get('portId')))
            port_group_details['port_list'] = port_list
            port_group_details.pop('symmetrixPortKey')

        metrics = self.enabled_metrics.get(pc.PORT_GROUP)
        port_group_performance = self.perf.get_port_group_stats(
            metrics=metrics, port_group_id=port_group_id,
            start_time=self.timestamp, end_time=self.timestamp)

        if not port_group_performance:
            msg = 'No Port Group performance data available.'
            self.log_warning(
                'Port Group: {p} | {m}'.format(p=port_group_id, m=msg))
            port_group_performance = {
                'pg_perf_details': False, 'pg_perf_message': msg}
        else:
            port_group_performance = self._process_performance_response(
                port_group_performance)

        return self._merge_dicts(port_group_details, port_group_performance)

    def get_active_host_set(self):
        """Get active hosts with performance metrics gathered.

        :returns: hosts -- set
        """
        active_hosts = self.perf.get_host_keys(
            start_time=self.timestamp, end_time=self.timestamp)
        active_host_list = list()
        for host in active_hosts:
            active_host_list.append(host.get('hostId'))

        return set(active_host_list)

    def get_host_details(self, host_id, active_host_set):
        """Get host details for a given host.

        :param host_id: host id -- str
        :param active_host_set: active hosts -- set
        :returns: host details -- JSON
        """
        self.log_debug(
            'Host: {h} | Collecting Host data.'.format(h=host_id))
        host_details = self.conn.provisioning.get_host(host_id)
        host_details['reporting_level'] = 'Host'

        # Change flags from comma separated string to list
        for f in ['enabled_flags', 'disabled_flags']:
            if host_details.get(f):
                host_details[f] = [
                    x.strip() for x in host_details[f].split(',')]
            else:
                host_details[f] = []

        host_performance = dict()
        active_host = False
        if host_id in active_host_set:
            active_host = True
            metrics = self.enabled_metrics.get(pc.HOST)
            host_performance = self.perf.get_host_stats(
                metrics=metrics, host_id=host_id, start_time=self.timestamp,
                end_time=self.timestamp)

        if not host_performance:
            if not active_host:
                msg = 'Host is not active, no performance data to collect.'
                log_func = self.log_debug
            else:
                msg = 'No Host performance data available.'
                log_func = self.log_warning

            log_func('Host: {h} | {m}'.format(h=host_id, m=msg))
            host_performance = {
                'host_perf_details': False, 'host_perf_message': msg,
                'performance_metrics': False}
        else:
            host_performance = self._process_performance_response(
                host_performance)
            host_performance['performance_metrics'] = True

        return self._merge_dicts(host_details, host_performance)

    def get_active_initiator_set(self):
        """Get active initiators with performance metrics gathered.

        :returns: initiators -- set
        """
        active_inits = self.perf.get_initiator_perf_keys(
            start_time=self.timestamp, end_time=self.timestamp)
        active_init_list = list()
        for init in active_inits:
            active_init_list.append(init.get('initiatorId'))

        return set(active_init_list)

    def get_initiator_details(self, initiator_id, active_initiator_set):
        """Get initiator details for a given initiator.

        :param initiator_id: initiator id -- str
        :param active_initiator_set: active initiators -- set
        :returns: initiator details -- JSON
        """
        self.log_debug(
            'Initiator: {i} | Collecting Initiator data.'.format(
                i=initiator_id))
        init_details = self.conn.provisioning.get_initiator(initiator_id)
        init_details['reporting_level'] = 'Initiator'

        # Convert director/port list of dicts to list of str
        dir_port_list = list()
        for dir_port in init_details.get('symmetrixPortKey'):
            dir_port_list.append('{d}:{p}'.format(
                d=dir_port.get('directorId'), p=dir_port.get('portId')))
        init_details['dir_port_keys'] = dir_port_list
        init_details.pop('symmetrixPortKey')

        if init_details.get('host'):
            init_details['host_id'] = init_details.get('host')
            init_details.pop('host')
        else:
            init_details['host_id'] = 'No Host associated'

        # Change flags from comma separated string to list
        for f in ['flags_in_effect', 'enabled_flags', 'disabled_flags']:
            if init_details.get(f):
                init_details[f] = [
                    x.strip() for x in init_details[f].split(',')]
            else:
                init_details[f] = []

        init_performance = dict()
        active_init = False
        if init_details.get('initiatorId') in active_initiator_set:
            active_init = True
            metrics = self.enabled_metrics.get(pc.INITIATOR)
            init_performance = self.perf.get_initiator_stats(
                metrics=metrics, initiator_id=init_details.get('initiatorId'),
                start_time=self.timestamp, end_time=self.timestamp)
        else:
            self.log_debug(
                'Initiator: {i} | Initiator is not active, no performance '
                'data to collect.'.format(i=initiator_id))

        if not init_performance:
            if init_details.get('type') == 'iSCSI':
                msg = 'No iSCSI Initiator performance data available.'
                log_func = self.log_debug
            elif not active_init:
                msg = 'No active Initiator performance data available.'
                log_func = self.log_debug
            else:
                msg = 'No Initiator performance data available.'
                log_func = self.log_warning

            log_func(
                'Initiator: {i} | {m}'.format(i=initiator_id, m=msg))
            init_performance = {
                'initiator_perf_details': False,
                'initiator_perf_message': msg,
                'performance_metrics': False}
        else:
            init_performance = self._process_performance_response(
                init_performance)
            init_performance['performance_metrics'] = True

        return self._merge_dicts(init_details, init_performance)

    def get_masking_view_details(self, masking_view_id):
        """Get Masking View details for a given Masking View.

        :param masking_view_id: masking view ID -- str
        :returns: masking view details -- JSON
        """
        self.log_debug(
            'MV: {m} | Collecting Masking View data.'.format(
                m=masking_view_id))
        mv_details = self.conn.provisioning.get_masking_view(masking_view_id)
        mv_details['reporting_level'] = 'Masking View'
        if not mv_details.get('hostId'):
            mv_details['hostId'] = 'None'
        if not mv_details.get('hostGroupId'):
            mv_details['hostGroupId'] = 'None'

        port_group_details = self.conn.provisioning.get_port_group(
            mv_details.get('portGroupId'))
        port_list = list()
        if port_group_details.get('symmetrixPortKey'):
            for dir_port in port_group_details.get('symmetrixPortKey'):
                port_list.append('{d}:{p}'.format(
                    d=dir_port.get('directorId'), p=dir_port.get('portId')))
            port_group_details['port_list'] = port_list
        mv_details['port_list'] = port_list

        metrics = self.enabled_metrics.get(pc.MASKING_VIEW)
        mv_performance = self.perf.get_masking_view_stats(
            metrics=metrics, masking_view_id=masking_view_id,
            start_time=self.timestamp, end_time=self.timestamp)

        if not mv_performance:
            msg = 'No Masking View performance data available.'
            self.log_warning(
                'MV: {mv} | {m}'.format(mv=masking_view_id, m=msg))
            mv_performance = {
                'mv_perf_details': False, 'mv_perf_message': msg}
        else:
            mv_performance = self._process_performance_response(
                mv_performance)

        return self._merge_dicts(mv_details, mv_performance)

    def get_masking_view_connections(self, masking_view_id):
        """Get connections for a given Masking View.

        :param masking_view_id: masking view ID -- str
        :returns: masking view connection details -- list
        """
        self.log_debug(
            'MV: {m} | Collecting Masking View connection data.'.format(
                m=masking_view_id))

        mv_details = self.conn.provisioning.get_masking_view(masking_view_id)
        if not mv_details.get('hostId'):
            mv_details['hostId'] = 'None'
        if not mv_details.get('hostGroupId'):
            mv_details['hostGroupId'] = 'None'

        mv_conn_details = self.conn.provisioning.get_masking_view_connections(
            masking_view_id)
        for mv_conn in mv_conn_details:
            mv_conn['reporting_level'] = 'Masking View Connection'

        response = list()
        for mv_conn in mv_conn_details:
            response.append(self._merge_dicts(mv_conn, mv_details))

        return response

    def get_ip_interface_list(self):
        """Get a list of IP interfaces.

        :returns: IP interfaces with dir/port keys --  list
        """
        iscsi_dir_list = self.conn.system.get_director_list(iscsi_only=True)
        iscsi_dir_ports = list()
        for iscsi_dir in iscsi_dir_list:
            port_list = self.conn.system.get_director_port_list(
                iscsi_dir)
            for port in port_list:
                ip_ints = self.conn.system.get_ip_interface_list(
                    director_id=port.get('directorId'),
                    port_id=port.get('portId'))
                if ip_ints:
                    iscsi_dir_ports.append({
                        'director_id': port.get('directorId'),
                        'port_id': port.get('portId'),
                        'ip_interface_list': ip_ints})

        return iscsi_dir_ports

    def get_ip_interface_details(self, director_id, port_id, interface_id):
        """Get IP interface details for a given dir/port/IP interface.

        :param director_id: director ID -- str
        :param port_id: port ID -- str
        :param interface_id: interface ID -- str
        :returns: IP interface details -- dict
        """
        self.log_debug(
            'IP Interface: {i} | Collecting IP Interface data.'.format(
                i=interface_id))
        int_details = self.conn.system.get_ip_interface(
            director_id, port_id, interface_id)
        int_details['reporting_level'] = 'IP Interface'
        int_details['director_id'] = director_id
        int_details['port_id'] = port_id

        dir_details = self.conn.system.get_director_port(
            director_id, str(int_details.get('iscsi_target_port')))
        dir_details = dir_details.get('symmetrixPort')
        int_details['iscsi_target_iqn'] = dir_details.get('identifier', 'None')

        int_key = '{d}:{p}:{n}:{ip}'.format(
            d=director_id, p=port_id, n=int_details.get('network_id'),
            ip=int_details.get('ip_address'))
        metrics = self.enabled_metrics.get(pc.IP_INTERFACE)
        int_performance = self.perf.get_ip_interface_stats(
            metrics=metrics, ip_interface_id=int_key,
            start_time=self.timestamp, end_time=self.timestamp)

        if not int_performance:
            msg = 'No IP Interface performance data available.'
            self.log_warning(
                'IP Interface: {i} | {m}'.format(i=interface_id, m=msg))
            int_performance = {
                'ip_interface_perf_details': False,
                'ip_interface_perf_message': msg}
        else:
            int_performance = self._process_performance_response(
                int_performance)
            int_performance.pop('ip_interface_id')

        return self._merge_dicts(int_details, int_performance)

    def get_iscsi_target_list(self):
        """Get list of iSCSI targets by dir/virtual port.

        :returns: iSCSI target dir/virtual port -- list
        """
        return self.conn.provisioning.get_port_list(
            filters={'iscsi_target': True})

    def get_iscsi_target_details(self, port_key):
        """Get iSCSI target details for a given dir/virtual port key.

        :param port_key: dir/virtual port -- dict
        :returns: iSCSI target details -- dict
        """
        director_id = port_key['directorId']
        port_id = port_key['portId']
        tgt_details = self.conn.system.get_director_port(
            director=director_id, port_no=port_id)

        tgt_details = tgt_details.get('symmetrixPort')
        tgt_details['reporting_level'] = 'iSCSI Target'
        tgt_details['port_id'] = port_id
        tgt_details['director_id'] = director_id
        tgt_details['dir_port_key'] = '{d}:{p}'.format(
            d=director_id, p=port_id)
        tgt_details.pop('symmetrixPortKey')

        self.log_debug(
            'iSCSI Tgt: {i} | Collecting iSCSI Target data.'.format(
                i=tgt_details.get('identifier')))

        metrics = self.enabled_metrics.get(pc.ISCSI_TARGET)
        tgt_performance = self.perf.get_endpoint_stats(
            metrics=metrics, endpoint_id=tgt_details.get('identifier'))

        if not tgt_performance:
            msg = 'No iSCSI target performance data available.'
            self.log_warning(
                'iSCSI Tgt: {i} | {m}'.format(
                    i=tgt_details.get('identifier'), m=msg))
            tgt_performance = {
                'iscsi_tgt_perf_details': False, 'iscsi_tgt_perf_message': msg}
        else:
            tgt_performance = self._process_performance_response(
                tgt_performance)

        return self._merge_dicts(tgt_details, tgt_performance)

    def get_rdf_group_map(self):
        """Get mapping of RDF groups and associated performance registrations.

        :returns: RDFG mapping with performance reg -- dict
        """
        rdfg_list = self.conn.replication.get_rdf_group_list()
        try:
            rdfs_list = self.perf.get_rdfs_keys()
        except exception.ResourceNotFoundException:
            self.log_debug('RDF Group | There are no configured RDFS Groups.')
            rdfs_list = list()
        try:
            rdfa_list = self.perf.get_rdfa_keys()
        except exception.ResourceNotFoundException:
            self.log_debug('RDF Group | There are no configured RDFS Groups.')
            rdfa_list = list()

        rdfg_mapping = dict()
        for rdfg in rdfg_list:
            rdfg_mapping[str(rdfg.get('rdfgNumber'))] = {
                'label': rdfg.get('label'), 'sync_perf': False,
                'async_perf': False}

        if rdfs_list:
            for rdfs in rdfs_list:
                rdfg_mapping[str(rdfs.get('raGroupId'))]['sync_perf'] = True
        if rdfa_list:
            for rdfa in rdfa_list:
                rdfg_mapping[str(rdfa.get('raGroupId'))]['async_perf'] = True

        return rdfg_mapping

    def get_rdf_group_details(self, rdf_group_number, rdf_group_map):
        """Return RDF group details for a given RDF group.

        :param rdf_group_number: RDFG number -- str
        :param rdf_group_map: RDFG mapping with performance reg -- dict
        :returns: RDFG details -- JSON
        """
        self.log_debug(
            'RDFG: {r} | Collecting RDF Group data.'.format(
                r=rdf_group_number))
        rdfg_details = self.conn.replication.get_rdf_group(rdf_group_number)
        rdfg_details = self._flatten_dict(rdfg_details)
        rdfg_details['reporting_level'] = 'RDF Group'

        rdfg_performance = dict()
        if rdf_group_map[rdf_group_number].get('sync_perf'):
            rdfg_details['rdfs'] = True
            metrics = self.enabled_metrics.get(pc.RDFS)
            rdfg_performance = self.perf.get_rdfs_stats(
                metrics=metrics, rdfs_group_id=rdf_group_number,
                start_time=self.timestamp, end_time=self.timestamp)
        elif rdf_group_map[rdf_group_number].get('async_perf'):
            rdfg_details['rdfa'] = True
            metrics = self.enabled_metrics.get(pc.RDFA)
            rdfg_performance = self.perf.get_rdfa_stats(
                metrics=metrics, rdfa_group_id=rdf_group_number,
                start_time=self.timestamp, end_time=self.timestamp)

        if not rdfg_performance:
            msg = 'No RDFG performance data available.'
            self.log_warning(
                'RDFG: {r} | {m}'.format(r=rdf_group_number, m=msg))
            rdfg_performance = {
                'rdfg_perf_details': False, 'rdfg_perf_message': msg}
        else:
            rdfg_performance = self._process_performance_response(
                rdfg_performance)

        return self._merge_dicts(rdfg_details, rdfg_performance)

    def get_rdf_pair_details(self, rdfg_data, device_id):
        """Return RDF device pair details for a given RDF pair.

        :param rdfg_data: RDF group data -- JSON
        :param device_id: RDF pair local device ID -- str
        :returns: RDF pair details -- JSON
        """
        rdfg_data_dict = json.loads(rdfg_data)
        rdfg_number = rdfg_data_dict.get('rdfg_number')
        self.log_debug(
            'RDFG: {r} | Collecting RDF Pair data.'.format(r=rdfg_number))
        pair_details = self.conn.replication.get_rdf_group_volume(
            rdfg_number, device_id)
        pair_details['reporting_level'] = 'RDF Pair'
        pair_details['type'] = rdfg_data_dict.get('type')
        pair_details['rdfg_label'] = rdfg_data_dict.get('label')

        return self._merge_dicts(pair_details)

    def get_metro_dr_environment_details(self, metro_dr_env_name):
        """Get Metro DR environment details.

        :param metro_dr_env_name: Metro DR environment name -- str
        :returns: Metro DR environment details -- JSON
        """
        self.log_debug(
            'Metro DR: {r} | Collecting Metro DR data.'.format(
                r=metro_dr_env_name))
        mdr_env_details = self.conn.metro_dr.get_metrodr_environment_details(
            environment_name=metro_dr_env_name)
        mdr_env_details['reporting_level'] = 'Metro DR'

        if mdr_env_details.get('environment_state'):
            env_state = mdr_env_details.get('environment_state')
            env_state = env_state.replace(',', '')
            env_state = env_state.replace(' ', '_')
            mdr_env_details['environment_state'] = env_state
        if mdr_env_details.get('dr_rdf_mode'):
            rdf_mode = mdr_env_details.get('dr_rdf_mode')
            rdf_mode = rdf_mode.replace(',', '')
            rdf_mode = rdf_mode.replace(' ', '_')
            mdr_env_details['dr_rdf_mode'] = rdf_mode

        return self._merge_dicts(mdr_env_details)

    def get_snapshot_policy_details(self, snap_policy_name):
        """Get Snapshot Policy details.

        :param snap_policy_name: Snapshot Policy name -- str
        :returns: Snapshot Policy details -- JSON
        """
        self.log_debug(
            'Snap Policy: {s} | Collecting Snapshot Policy data.'.format(
                s=snap_policy_name))
        sp_details = self.conn.snapshot_policy.get_snapshot_policy(
            snap_policy_name)
        sp_details['reporting_level'] = 'Snapshot Policy'

        if sp_details.get('provider_name'):
            sp_details['policy_type'] = 'cloud'
        else:
            sp_details['policy_type'] = 'local'
            sp_details['provider_name'] = 'N/A'

        return self._merge_dicts(sp_details)

    def get_alert_list(self):
        """Get a list of alerts from Unisphere.

        :returns: alert IDs -- list
        """
        return self.conn.system.get_alert_ids(array=self.array_id)

    def get_alert(self, alert_id):
        """Get alert ID details.

        :param alert_id: alert ID -- str
        :returns: alert details -- dict
        """
        self.log_debug(
            'Alert: {a} | Collecting Alert data.'.format(a=alert_id))
        alert_details = self.conn.system.get_alert_details(alert_id)

        alert_response = {
            'reporting_level': 'Alert',
            'array_id': alert_details.get('array'),
            'asset_id': alert_details.get('object'),
            'timestamp': self.timestamp,
            'u4v_source': self.helper.get_arg('u4v_ip_address')}

        return self._merge_dicts(alert_details, alert_response)

    def get_audit_log_record_list(self):
        """Get a list of audit record from the current timestamp - interval.

        :returns: record IDs -- list
        """
        audit_list = self.conn.system.get_audit_log_list(
            start_time=self.timestamp - (self.interval * 1000),
            end_time=self.timestamp)

        return [x.get('record_id') for x in audit_list]

    def get_audit_log_record_details(self, record_id):
        """Get audit log details for a given audit record ID.

        :param record_id: audit record id -- str
        :returns: record details -- JSON
        """
        self.log_debug(
            'Audit Log: {a} | Collecting Audit Log data.'.format(a=record_id))
        record_details = self.conn.system.get_audit_log_record(record_id)
        record_details['reporting_level'] = 'Audit Log'

        if not record_details.get('username'):
            record_details['username'] = 'None'
        if not record_details.get('activity_id'):
            record_details['activity_id'] = 'None'
        # We need to change \ to / because of issues working with non-escaped
        # chars in Splunk
        if '\\' in record_details.get('username'):
            formatted_username = record_details['username'].replace('\\', '/')
            record_details['username'] = formatted_username

        if record_details.get('message'):
            record_details['message'] = record_details['message'].strip()

        # We want to use the timestamp from the audit log instead of the
        # usual interval timestamp, convert to milliseconds since epoch
        timestamp = None
        if record_details.get('entry_date'):
            timestamp = record_details.get('entry_date') * 1000

        return self._merge_dicts(record_details, timestamp=timestamp)
