# Copyright (c) 2020 Dell Inc. or its subsidiaries.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""system.py."""

import logging
import re
import time

from datetime import datetime
from pathlib import Path

from PyU4V.common import CommonFunctions
from PyU4V.utils import constants
from PyU4V.utils import exception
from PyU4V.utils import file_handler
from PyU4V.utils import time_handler

LOG = logging.getLogger(__name__)

ARRAY_ID = constants.ARRAY_ID
ARRAY_NUM = constants.ARRAY_NUM
DESCRIPTION = constants.DESCRIPTION
DISK = constants.DISK
FAILED = constants.FAILED
HEALTH = constants.HEALTH
HEALTH_CHECK = constants.HEALTH_CHECK
SG_ID = constants.SG_ID
SG_NUM = constants.SG_NUM
SYMMETRIX = constants.SYMMETRIX
SYSTEM = constants.SYSTEM
TAG = constants.TAG
TAG_NAME = constants.TAG_NAME
ALERT = constants.ALERT
ALERT_SUMMARY = constants.ALERT_SUMMARY
SETTINGS_FILENAME_TEMPLATE = constants.SETTINGS_FILENAME_TEMPLATE
AUDIT_LOG_FILENAME_TEMPLATE = constants.AUDIT_LOG_FILENAME_TEMPLATE
SETTINGS = constants.SETTINGS
EXPORT_FILE = constants.EXPORT_FILE
IMPORT_FILE = constants.IMPORT_FILE
SRC_ARRAY = constants.SRC_ARRAY
TGT_ARRAYS = constants.TGT_ARRAYS
FILE_PASSWORD = constants.FILE_PASSWORD
ZIP_FILE = constants.ZIP_FILE
ZIP_SUFFIX = constants.ZIP_SUFFIX
PDF_SUFFIX = constants.PDF_SUFFIX
FILE_READ_MODE = constants.FILE_READ_MODE
FILE_WRITE_MODE = constants.FILE_WRITE_MODE
ALL_SETTINGS = constants.ALL_SETTINGS
EXCLUDE_UNI_SETTINGS = constants.EXCLUDE_UNI_SETTINGS
EXCLUDE_SYS_SETTINGS = constants.EXCLUDE_SYS_SETTINGS
UNI_ALERT_SETTINGS = constants.UNI_ALERT_SETTINGS
UNI_PERF_PREF_SETTINGS = constants.UNI_PERF_PREF_SETTINGS
UNI_PERF_USER_SETTINGS = constants.UNI_PERF_USER_SETTINGS
UNI_PERF_METRIC_SETTINGS = constants.UNI_PERF_METRIC_SETTINGS
SYS_ALERT_SETTINGS = constants.SYS_ALERT_SETTINGS
SYS_ALERT_NOTIFI_SETTINGS = constants.SYS_ALERT_NOTIFI_SETTINGS
SYS_THRESH_SETTINGS = constants.SYS_THRESH_SETTINGS
SYS_PERF_THRESH_SETTINGS = constants.SYS_PERF_THRESH_SETTINGS
AUDIT_LOG_RECORD = constants.AUDIT_LOG_RECORD
COUNT = constants.COUNT
AUDIT_LOG_FILENAME = constants.AUDIT_LOG_FILENAME
BINARY_DATA = constants.BINARY_DATA
AUDIT_RECORD_PATH = constants.AUDIT_RECORD_PATH
SUCCESS = constants.SUCCESS
AUDIT_RECORD_TIME = constants.AUDIT_RECORD_TIME
STR_TIME_FORMAT = constants.STR_TIME_FORMAT
DIRECTOR = constants.DIRECTOR
DIRECTOR_ID = constants.DIRECTOR_ID
PORT = constants.PORT
IP_INTERFACE = constants.IP_INTERFACE
IP_INTERFACE_ID = constants.IP_INTERFACE_ID


class SystemFunctions(object):
    """SystemFunctions."""

    def __init__(self, array_id, rest_client):
        """__init__."""
        self.common = CommonFunctions(rest_client)
        self.array_id = array_id

    def get_system_health(self, array_id=None):
        """Query for system health information.

        :param array_id: array id -- str
        :returns: system health -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM, resource_level=SYMMETRIX,
            resource_level_id=array_id, object_type=HEALTH)

    def list_system_health_check(self, array_id=None):
        """List previously run system health checks.

        :param array_id: array id -- str
        :returns: system health checks -- list
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            object_type=HEALTH, object_type_id=HEALTH_CHECK)

    def get_health_check_details(self, health_check_id, array_id=None):
        """Gets details of individual health check.

        :param health_check_id: health check id -- str
        :param array_id: array id -- str
        :returns: health check details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=HEALTH, resource_type_id=HEALTH_CHECK,
            object_type=health_check_id)

    def perform_health_check(self, array_id=None, description=None):
        """Initiate a environmental health check.

        :param array_id: array id -- str
        :param description: description for health check, if not set this will
                            default to 'PyU4V-array_id-date-time' -- str
        :returns: health check property details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        now = datetime.now()
        date_now, time_now = now.strftime('%d%m%Y'), now.strftime('%H%M%S')
        if not description:
            description = 'PyU4V-{arr}-{date}-{time}'.format(
                arr=array_id, date=date_now, time=time_now)
        return self.common.create_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            object_type=HEALTH, object_type_id=HEALTH_CHECK,
            payload={DESCRIPTION: description})

    def delete_health_check(self, health_check_id, array_id=None):
        """Delete a health check record.

        :param health_check_id: health check id -- str
        :param array_id: array id -- str
        """
        array_id = self.array_id if not array_id else array_id
        self.common.delete_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=HEALTH, resource_type_id=HEALTH_CHECK,
            object_type=health_check_id)

    def get_disk_id_list(self, array_id=None, failed=False):
        """Get a list of disks ids installed.

        :param array_id: array id -- str
        :param failed: if only failed disks should be returned -- bool
        :returns: disk ids -- list
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=DISK, params={FAILED: failed})

    def get_disk_details(self, disk_id, array_id=None):
        """Get details for specified disk id.

        :param disk_id: disk id -- str
        :param array_id: array id -- str
        :returns: disk details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        return self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=DISK, resource_type_id=disk_id)

    def get_tags(self, array_id=None, tag_name=None, storage_group_id=None,
                 num_of_storage_groups=None, num_of_arrays=None):
        """Query for a list of tag names.

        The input parameters represent optional filters for the tag query,
        including any filters will apply that filter to the list of returned
        tags.

        :param array_id: filter by array id -- str
        :param tag_name: filter by tag name -- str
        :param storage_group_id: filter by storage group id -- str
        :param num_of_storage_groups: filter by tags that are in x or greater
                                      amount of storage groups -- int
        :param num_of_arrays: filter by tags that in y or greater amount of
                              arrays -- int
        :returns: tags -- list
        """
        filters = dict()
        if array_id:
            filters[ARRAY_ID] = array_id
        if tag_name:
            filters[TAG_NAME] = tag_name
        if storage_group_id:
            filters[SG_ID] = storage_group_id
        if num_of_storage_groups:
            filters[SG_NUM] = str(num_of_storage_groups)
        if num_of_arrays:
            filters[ARRAY_NUM] = str(num_of_arrays)

        return self.common.get_resource(
            category=SYSTEM, resource_level=TAG, params=filters)

    def get_tagged_objects(self, tag_name):
        """Get a list of objects with specified tag.

        :param tag_name: tag name -- str
        :returns: tags -- list
        """
        return self.common.get_resource(
            category=SYSTEM, resource_level=TAG, resource_level_id=tag_name)

    def get_alert_summary(self):
        """Gets Alert Summary information.

        :returns: summary of alerts on system - dict
        """
        return self.common.get_resource(
            category=SYSTEM, resource_level=ALERT_SUMMARY)

    def get_alert_ids(self, array=None, _type=None, severity=None, state=None,
                      created_date=None, _object=None, object_type=None,
                      acknowledged=False, description=None):
        """Get a list of Alert Ids.

        Parameters for this function can be combined to create a search pattern
        based on multiple filters to target results.

        :param array: filters returned list to display Alert Ids that are
                      associated with the specified array e.g. "000213234443"
                      or "<like>443"
                      -- str
        :param _type: filters returned list to display Alert Ids that has the
                     following type: ARRAY, PERFORMANCE, SERVER
        :param severity: filters returned list to display only Alert Ids with
                         specified severity: NORMAL, INFORMATION, MINOR,
                         WARNING, CRITICAL, FATAL -- str
        :param state: filters returned list to display Alert Ids that has the
                      following state: NEW, ACKNOWLEDGED, CLEARED -- str
        :param created_date: filters returned list to display Alert Ids that
                             are greater than(">1"), Less than("<1") or equal
                             to the specified created_date
                             "MMM-dd-yyyy HH:mm:ss.SSS" -- str
        :param _object: filters returned list to display
                       Alert Ids that are associated with the specified array
                       object e.g. equal to "object=SRP_3" -- str
        :param object_type: filters returned list to display Alert Ids that are
                            associated with the specified array object type
                            e.g. equal to "object_type=Director" -- str
        :param acknowledged: filters returned list to display Alert Ids that
                             are acknowledged or not -- bool
        :param description: filters returned list to contain text matching
                            description in body -- str
        :returns: list of alert ids -- list
        """
        filters = dict()
        filters['acknowledged'] = acknowledged

        if array:
            filters['array'] = array
        if _type:
            filters['type'] = _type
        if severity:
            filters['severity'] = severity
        if state:
            filters['state'] = state
        if created_date:
            filters['created_date'] = created_date
        if _object:
            filters['_object'] = _object
        if object_type:
            filters['object_type'] = object_type
        if description:
            filters['description'] = description
        response = self.common.get_resource(
            category=SYSTEM, resource_level=ALERT, params=filters)
        return response.get('alertId') if response else list()

    def get_alert_details(self, alert_id):
        """Gets the details of an alert.

        :param alert_id: alert_id uniquely identifying alert on Unisphere
                         system -- str
        :returns: alert details -- dict
        """
        return self.common.get_resource(
            category=SYSTEM, resource_level=ALERT,
            resource_level_id=alert_id)

    def acknowledge_alert(self, alert_id):
        """Acknowledges an alert.

        :param alert_id: alert_id uniquely identifying alert on Unisphere
                         system --str
        :returns: alert details -- dict
        """
        payload = {'editAlertActionParam': 'ACKNOWLEDGE'}

        return self.common.modify_resource(
            category=SYSTEM, resource_level=ALERT,
            resource_level_id=alert_id, payload=payload)

    def delete_alert(self, alert_id):
        """Deletes Specified Alert.

        :param alert_id: alert_id uniquely identifying alert on Unisphere
                         system --str
        """
        return self.common.delete_resource(
            category=SYSTEM, resource_level=ALERT,
            resource_level_id=alert_id)

    def _download_settings(
            self, request_body, file_name=None, dir_path=None,
            return_binary=False):
        """Download settings helper method.

        :param request_body: payload request body -- dict
        :param file_name: zip file name -- str
        :param dir_path: file save location -- str
        :param return_binary: return settings binary data -- bool
        :returns: export details -- dict
        """
        date_time = datetime.fromtimestamp(time.time())

        if not file_name:
            file_name = '{fn}-{d}.{e}'.format(
                fn=SETTINGS_FILENAME_TEMPLATE,
                d=date_time.strftime(STR_TIME_FORMAT),
                e=ZIP_SUFFIX)

        response = self.common.download_file(
            category=SYSTEM, resource_level=SETTINGS,
            resource_type=EXPORT_FILE, payload=request_body)

        return_dict = {'success': False}

        if response:
            # Return binary data, do not write to file
            if return_binary:
                return_dict['binary_data'] = response.content
            # Write to file
            else:
                file_path = file_handler.write_binary_data_to_file(
                    data=response, file_extension=ZIP_SUFFIX,
                    file_name=file_name, dir_path=dir_path)
                return_dict['settings_path'] = file_path

            return_dict['success'] = True
            return_dict['settings_time'] = date_time
            LOG.info('The settings download request was successful.')

        return return_dict

    def download_all_settings(
            self, file_password, dir_path=None, file_name=None, array_id=None,
            return_binary=False):
        """Download all settings.

        Export settings feature allows the saving of a subset of system
        settings to a file. The exported settings have a generic format and do
        not contain any specific information regarding particular storage array
        or Unisphere instance, thus making it applicable in any environment.

        The intention is to help users to port the system wide settings to
        another instance of Unisphere, and also to capture single array
        settings so that they can be applied to another storage array within
        single instance or another instance of Unisphere at any point of time.

        - All settings:
            - Unisphere settings:
                - Alert notifications
                - Performance metrics
                - Performance preferences
                - Performance user templates
            - System settings:
                - Alert policies
                - Alert level notifications
                - Performance thresholds
                - System thresholds

        By default settings will be written to a zip file in the current
        working directory unless a supplied directory path and/or file name
        are provided. If any extension is provided in the file name it will be
        replaced with .zip before the data is written to file.

        If instead the file writing process should be handled outside of PyU4V
        or uploaded directly to Unisphere without any file handling set
        return_binary to True. The response dict will have the settings
        binary data included in key 'binary_data'.

        :param file_password: password to sign file (required) -- str
        :param dir_path: file save location -- str
        :param file_name: zip file name -- str
        :param array_id: array id -- str
        :param return_binary: return settings binary data -- bool
        :returns: download details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        request_body = {FILE_PASSWORD: file_password,
                        SRC_ARRAY: array_id}
        return self._download_settings(
            request_body=request_body, dir_path=dir_path,
            file_name=file_name, return_binary=return_binary)

    def download_unisphere_settings(
            self, file_password, dir_path=None, file_name=None,
            return_binary=False, exclude_alert_notification_settings=False,
            exclude_performance_preference_settings=False,
            exclude_performance_user_templates=False,
            exclude_performance_metric_settings=False):
        """Download Unisphere settings.

        - Unisphere settings:
            - Alert notifications
            - Performance metrics
            - Performance preferences
            - Performance user templates

        By default settings will be written to a zip file in the current
        working directory unless a supplied directory path and/or file name
        are provided. If any extension is provided in the file name it will be
        replaced with .zip before the data is written to file.

        If instead the file writing process should be handled outside of PyU4V
        or uploaded directly to Unisphere without any file handling set
        return_binary to True. The response dict will have the settings
        binary data included in key 'binary_data'.

        :param file_password: password to sign file (required) -- str
        :param dir_path: file save location -- str
        :param file_name: zip file name -- str
        :param return_binary: return settings binary data -- bool
        :param exclude_alert_notification_settings: exclude alert notification
                                                    settings -- bool
        :param exclude_performance_preference_settings: exclude performance
                                                        preference settings
                                                        -- bool
        :param exclude_performance_user_templates: exclude performance user
                                                   templates -- bool
        :param exclude_performance_metric_settings: exclude performance
                                                    metric settings
        :returns: download details -- dict
        """
        if False not in [exclude_alert_notification_settings,
                         exclude_performance_preference_settings,
                         exclude_performance_user_templates,
                         exclude_performance_metric_settings]:
            msg = ('Invalid Unisphere settings input parameters supplied, at '
                   'least one settings category must be not be excluded in '
                   'the input parameters.')
            LOG.error(msg)
            raise exception.InvalidInputException(msg)

        exclusion_list = list()
        if exclude_alert_notification_settings:
            exclusion_list.append(UNI_ALERT_SETTINGS)
        if exclude_performance_preference_settings:
            exclusion_list.append(UNI_PERF_PREF_SETTINGS)
        if exclude_performance_user_templates:
            exclusion_list.append(UNI_PERF_USER_SETTINGS)
        if exclude_performance_metric_settings:
            exclusion_list.append(UNI_PERF_METRIC_SETTINGS)

        request_body = {FILE_PASSWORD: file_password,
                        SRC_ARRAY: self.array_id,
                        EXCLUDE_SYS_SETTINGS: [ALL_SETTINGS],
                        EXCLUDE_UNI_SETTINGS: exclusion_list}

        return self._download_settings(
            request_body=request_body, dir_path=dir_path,
            file_name=file_name, return_binary=return_binary)

    def download_system_settings(
            self, file_password, dir_path=None, file_name=None, array_id=None,
            return_binary=False, exclude_alert_policy_settings=False,
            alert_level_notification_settings=False,
            exclude_system_threshold_settings=False,
            exclude_performance_threshold_settings=False):
        """Export System settings.

        - System settings:
            - Alert policies
            - Alert level notifications
            - Performance thresholds
            - System thresholds

        By default settings will be written to a zip file in the current
        working directory unless a supplied directory path and/or file name
        are provided. If any extension is provided in the file name it will be
        replaced with .zip before the data is written to file.

        If instead the file writing process should be handled outside of PyU4V
        or uploaded directly to Unisphere without any file handling set
        return_binary to True. The response dict will have the settings
        binary data included in key 'binary_data'.

        :param file_password: password to sign file (required) -- str
        :param dir_path: file save location -- str
        :param file_name: zip file name -- str
        :param array_id: array id -- str
        :param return_binary: return settings binary data -- bool
        :param exclude_alert_policy_settings: exclude alert policy settings
                                              -- bool
        :param alert_level_notification_settings: exclude alert level
                                          notification settings -- bool
        :param exclude_system_threshold_settings: exclude system threshold
                                                  settings -- bool
        :param exclude_performance_threshold_settings: exclude performance
                                                       threshold settings
                                                       -- bool
        :returns: export details -- dict
        """
        if False not in [exclude_alert_policy_settings,
                         exclude_system_threshold_settings,
                         exclude_performance_threshold_settings,
                         alert_level_notification_settings]:
            msg = ('Invalid system settings input parameters supplied, at '
                   'least one settings category must be not be excluded in '
                   'the input parameters.')
            LOG.error(msg)
            raise exception.InvalidInputException(msg)

        exclusion_list = list()
        if exclude_alert_policy_settings:
            exclusion_list.append(SYS_ALERT_SETTINGS)
        if alert_level_notification_settings:
            exclusion_list.append(SYS_ALERT_NOTIFI_SETTINGS)
        if exclude_system_threshold_settings:
            exclusion_list.append(SYS_THRESH_SETTINGS)
        if exclude_performance_threshold_settings:
            exclusion_list.append(SYS_PERF_THRESH_SETTINGS)

        array_id = self.array_id if not array_id else array_id
        request_body = {FILE_PASSWORD: file_password,
                        SRC_ARRAY: array_id,
                        EXCLUDE_SYS_SETTINGS: exclusion_list,
                        EXCLUDE_UNI_SETTINGS: [ALL_SETTINGS]}

        return self._download_settings(
            request_body=request_body, dir_path=dir_path,
            file_name=file_name, return_binary=return_binary)

    def upload_settings(self, file_password, file_path=None, array_id=None,
                        binary_data=None):
        """Upload Unisphere and/or system settings to Unisphere.

        Allows for importing a zip file or binary data that contains settings
        that were previously exported from Unisphere.

        The settings that a file upload may include are:

        - All settings:
            - Unisphere settings:
                - Alert notifications
                - Performance metrics
                - Performance preferences
                - Performance user templates
            - System settings:
                - Alert policies
                - Alert level notifications
                - Performance thresholds
                - System thresholds

        A password that was specified during export needs to be provided during
        import operation. This is to assure that the imported file has not been
        tampered with.

        It is possible to upload system settings for more than one array, to
        do so pass a list of array IDs in to array_id input parameter. For
        Unisphere settings an array ID is not required.

        :param file_password: password that file has been signed with -- str
        :param file_path: full file location -- str
        :param array_id: array id -- str
        :param binary_data: binary settings data -- bytes
        :returns: upload details -- dict
        """
        # Work around: We need to provide the array ID for all upload requests
        array_id = self.array_id if not array_id else array_id
        array_id = ','.join(array_id) if isinstance(
            array_id, list) else array_id

        if binary_data:
            try:
                assert isinstance(binary_data, bytes) is True
                data = binary_data
            except AssertionError as error:
                msg = ('You must provide valid bytes data before upload to '
                       'Unisphere can proceed.')
                LOG.error(msg)
                raise exception.InvalidInputException(msg) from error
        else:
            try:
                f_path = Path(file_path)
                assert f_path.is_file() is True
                LOG.info('Uploading settings from {p}'.format(p=f_path))
                data = open(f_path, FILE_READ_MODE)
            except (TypeError, AssertionError) as error:
                msg = (
                    'Invalid file path supplied for settings upload '
                    'location: {f}'.format(f=file_path))
                LOG.error(msg)
                raise exception.InvalidInputException(msg) from error

        form_data = {ZIP_FILE: data, TGT_ARRAYS: array_id,
                     FILE_PASSWORD: file_password}

        return self.common.upload_file(
            category=SYSTEM, resource_level=SETTINGS,
            resource_type=IMPORT_FILE, form_data=form_data)

    def get_audit_log_list(
            self, start_time, end_time, array_id=None, user_name=None,
            host_name=None, client_host=None, message=None, record_id=None,
            activity_id=None, application_id=None, application_version=None,
            task_id=None, process_id=None, vendor_id=None, os_type=None,
            os_revision=None, api_library=None, api_version=None,
            audit_class=None, action_code=None, function_class=None):
        """Get a list of audit logs from Unisphere between start and end date.

        Retrieve a list of audit logs from Unisphere, it is possible to filter
        this list through the input parameters. Due to the potential to return
        large amounts of results both start and end time are required.

        :param start_time: timestamp in milliseconds since epoch -- int
        :param end_time: timestamp in milliseconds since epoch -- int
        :param array_id: array serial number -- str
        :param user_name: Optional value that filters returned list to display
                          Audit Log Entries that contain the specified username
                          only -- str
        :param host_name: Optional value that filters returned list to display
                          Audit Log Entries that contain the specified
                          host_name only -- str
        :param client_host: Optional value that filters returned list to
                            display Audit Log Entries that contain the
                            specified client_host only -- str
        :param message: Optional value that filters returned list to display
                        Audit Log Entries that contain the specified message
                        only -- str
        :param record_id: Optional value that filters returned list to display
                          Audit Log Entries that have a matching
                          record_id -- int
        :param activity_id: Optional value that filters returned list to
                            display Audit Log Entries that contain the
                            specified activity_id only -- str
        :param application_id: Optional value that filters returned list to
                               display Audit Log Entries that contain the
                               specified application_id only -- str
        :param application_version: Optional value that filters returned list
                                    to display Audit Log Entries that contain
                                    the specified application_version
                                    only -- str
        :param task_id: Optional value that filters returned list to display
                        Audit Log Entries that contain the specified task_id
                        only -- str
        :param process_id: Optional value that filters returned list to display
                           Audit Log Entries that contain the specified
                           process_id only -- str
        :param vendor_id: Optional value that filters returned list to display
                          Audit Log Entries that contain the specified
                          vendor_id only -- str
        :param os_type: Optional value that filters returned list to display
                        Audit Log Entries that contain the specified os_type
                        only -- str
        :param os_revision: Optional value that filters returned list to
                            display Audit Log Entries that contain the
                            specified os_revision only -- str
        :param api_library: Optional value that filters returned list to
                            display Audit Log Entries that contain the
                            specified api_library only -- str
        :param api_version: Optional value that filters returned list to
                            display Audit Log Entries that contain the
                            specified api_version only -- str
        :param audit_class: Optional value that filters returned list to
                            display Audit Log Entries that contain the
                            specified audit_class only -- str
        :param action_code: Optional value that filters returned list to
                            display Audit Log Entries that contain the
                            specified action_code only -- str
        :param function_class: Optional value that filters returned list to
                               display Audit Log Entries that contain the
                               specified function_class only -- str
        :returns: audit logs -- list
        """
        array_id = self.array_id if not array_id else array_id
        start_time = time_handler.format_time_input(
            start_time, return_seconds=True)
        end_time = time_handler.format_time_input(
            end_time, return_seconds=True)

        # If the time delta is longer than 24 hours...
        if (end_time - start_time) > (60 * 60 * 24):
            LOG.warning(
                'It is not recommended that queries with large time ranges '
                'are used to retrieve system audit logs. Please consider '
                'refining your search. If large time ranges are required, '
                'please use sparingly and not in frequently run scripts.')

        target_uri = self.common.build_target_uri(
            category=SYSTEM, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=AUDIT_LOG_RECORD)

        # Form query params manually until audit log endpoint is updated to
        # accept a dict of filter params - limited due to requirement of more
        # than one instance of the same parameter key which is not possible
        # with python dictionaries
        query_uri = '?'
        query_uri += 'entry_date=>{start}&entry_date=<{end}'.format(
            start=start_time, end=end_time)

        if user_name:
            query_uri += '&user_name={x}'.format(x=user_name)
        if host_name:
            query_uri += '&host_name={x}'.format(x=host_name)
        if client_host:
            query_uri += '&client_host={x}'.format(x=client_host)
        if message:
            query_uri += '&message={x}'.format(x=message)
        if record_id:
            query_uri += '&record_id={x}'.format(x=record_id)

        if activity_id:
            query_uri += '&activity_id={x}'.format(x=activity_id)
        if application_id:
            query_uri += '&application_id={x}'.format(x=application_id)
        if application_version:
            query_uri += '&application_version={x}'.format(
                x=application_version)
        if task_id:
            query_uri += '&task_id={x}'.format(x=task_id)
        if process_id:
            query_uri += '&process_id={x}'.format(x=process_id)

        if vendor_id:
            query_uri += '&vendor_id={x}'.format(x=vendor_id)
        if os_type:
            query_uri += '&os_type={x}'.format(x=os_type)
        if os_revision:
            query_uri += '&os_revision={x}'.format(x=os_revision)
        if api_library:
            query_uri += '&api_library={x}'.format(x=api_library)
        if api_version:
            query_uri += '&api_version={x}'.format(x=api_version)

        if audit_class:
            query_uri += '&audit_class={x}'.format(x=audit_class)
        if action_code:
            query_uri += '&action_code={x}'.format(x=action_code)
        if function_class:
            query_uri += '&function_class={x}'.format(x=function_class)

        if query_uri != '?':
            target_uri += query_uri

        response = self.common.get_request(target_uri=target_uri,
                                           resource_type=AUDIT_LOG_RECORD)

        if response.get(COUNT, 0) > 0:
            return self.common.get_iterator_results(response)
        else:
            return list()

    def get_audit_log_record(self, record_id, array_id=None):
        """Get audit log details for a specific record.

        :param record_id: audit log record id -- int
        :param array_id: array serial number -- str
        :returns: audit log record details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        target_uri = self.common.build_target_uri(
            category=SYSTEM, resource_level=SYMMETRIX,
            resource_level_id=array_id, resource_type=AUDIT_LOG_RECORD,
            resource_type_id=record_id)

        response = self.common.get_request(
            target_uri=target_uri, resource_type=AUDIT_LOG_RECORD)

        return response

    def download_audit_log_record(self, array_id=None, return_binary=False,
                                  dir_path=None, file_name=None):
        """Download audit log record for the last week in PDF

        :param array_id: array serial number -- str
        :param return_binary: return binary data instead of writing audit log
                              record pdf to file -- bool
        :param dir_path: file write directory path -- str
        :param file_name: file name -- str
        :returns: download details -- dict
        """
        array_id = self.array_id if not array_id else array_id
        date_time = datetime.fromtimestamp(time.time())

        if not file_name:
            file_name = '{fn}-{d}.{e}'.format(
                fn=AUDIT_LOG_FILENAME_TEMPLATE,
                d=date_time.strftime(STR_TIME_FORMAT),
                e=PDF_SUFFIX)

        req_body = {AUDIT_LOG_FILENAME: file_name}

        response = self.common.download_file(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=AUDIT_LOG_RECORD,
            resource=EXPORT_FILE, payload=req_body)

        return_dict = dict()

        # Return binary data, do not write to file
        if return_binary:
            return_dict[BINARY_DATA] = response.content
        # Write to file
        else:
            file_path = file_handler.write_binary_data_to_file(
                data=response, file_extension=PDF_SUFFIX, file_name=file_name,
                dir_path=dir_path)
            return_dict[AUDIT_RECORD_PATH] = file_path

        return_dict[SUCCESS] = True
        return_dict[AUDIT_RECORD_TIME] = date_time
        LOG.info('The audit log download request was successful.')

        return return_dict

    def get_director_list(self, array_id=None, iscsi_only=False):
        """Get a list of directors for a given array.

        :param array_id: array serial number -- str
        :param iscsi_only: return only iSCSI directors -- bool
        :returns: iSCSI directors -- list
        """
        array_id = array_id if array_id else self.array_id
        dir_list = self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=DIRECTOR)
        response_dir_list = list()
        for director in dir_list.get(DIRECTOR_ID, list()):
            if iscsi_only and re.match(r'^SE-\d[A-Z]$', director):
                response_dir_list.append(director)
            elif not iscsi_only:
                response_dir_list.append(director)

        return response_dir_list

    def get_director_port_list(self, director_id, array_id=None,
                               iscsi_target=None):
        """Get a list of director ports for a specified director.

        :param director_id: director id -- str
        :param array_id: array id -- str
        :param iscsi_target: if the port is an iSCSI target, applicable to
                             front-end SE directors only, default to not set
                             -- bool
        :returns: director ports -- list
        """
        array_id = array_id if array_id else self.array_id

        filters = dict()
        if isinstance(iscsi_target, bool):
            filters['iscsi_target'] = iscsi_target

        port_list = self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=DIRECTOR, resource_type_id=director_id,
            resource=PORT, params=filters)
        return port_list.get(
            'symmetrixPortKey', list()) if port_list else list()

    def get_ip_interface_list(self, director_id, port_id, array_id=None):
        """Get a list of IP interfaces for a given array.

        :param director_id: director id -- str
        :param port_id: port id -- str
        :param array_id: array id -- str
        :returns: IP interfaces -- list
        """
        array_id = array_id if array_id else self.array_id
        ip_list = self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=DIRECTOR, resource_type_id=director_id,
            resource=PORT, resource_id=port_id, object_type=IP_INTERFACE)

        return ip_list.get(IP_INTERFACE_ID, list()) if ip_list else list()

    def get_ip_interface(self, director_id, port_id, interface_id,
                         array_id=None):
        """Get IP interface details

        :param director_id: director id -- str
        :param port_id: port id -- str
        :param interface_id: interface id -- str
        :param array_id: array id -- str
        :returns: IP interface details -- dict
        """
        array_id = array_id if array_id else self.array_id
        interface = self.common.get_resource(
            category=SYSTEM,
            resource_level=SYMMETRIX, resource_level_id=array_id,
            resource_type=DIRECTOR, resource_type_id=director_id,
            resource=PORT, resource_id=port_id,
            object_type=IP_INTERFACE, object_type_id=interface_id)

        return interface if interface else dict()
