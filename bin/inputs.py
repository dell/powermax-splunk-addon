"""bin/inputs.py"""
import ta_dellemc_vmax_declare

import os
import sys
import time
import datetime
import json

import modinput_wrapper.base_modinput
from splunklib import modularinput as smi

import powermax_splunk_core.driver.powermax_input_module as input_module

bin_dir = os.path.basename(__file__)


class ModInputinputs(modinput_wrapper.base_modinput.BaseModInput):

    def __init__(self):
        super(ModInputinputs, self).__init__(
            'ta_dellemc_vmax', 'inputs', False)
        self.global_checkbox_fields = None

    def get_scheme(self):
        """Overloaded splunklib modular input method."""
        scheme = super(ModInputinputs, self).get_scheme()
        scheme.title = 'VMAX/PowerMax'
        scheme.description = (
            'Go to the add-on\'s configuration UI and configure modular '
            'inputs under the Inputs menu.')
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True

        # Add-on configuration options
        scheme.add_argument(smi.Argument(
            'name', title='Name', description='', required_on_create=True))
        scheme.add_argument(smi.Argument(
            'u4v_ip_address', title='Unisphere IP Address', description='',
            required_on_create=True, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'u4v_port', title='Unisphere Port',
            description='Unisphere default port is 8443',
            required_on_create=True, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'u4v_username', title='Unisphere Username', description='',
            required_on_create=True, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'u4v_password', title='Unisphere Password', description="",
            required_on_create=True, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'u4v_vmax_id', title='Array ID',
            description='This is the 12-digit array ID',
            required_on_create=True, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'enable_ssl', title='Enable SSL',
            description=(
                'Enable SSL communication between Splunk and Unisphere.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'ssl_cert_location', title='SSL Cert Location',
            description=(
                '(Optional) Leave this blank if the Unisphere SSL certificate '
                'is loaded into the system, otherwise you can specify the '
                'direct path to the .pem certificate'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'rest_request_timeout', title='REST Request Timeout',
            description=(
                '(Optional) Default REST request timeout value in seconds, '
                'default is 60, for more information please consult the TA '
                'user guide'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_array', title='Array',
            description='Collect Array level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_array_metrics', title='Array Custom Metrics',
            description=(
                '(Optional) For custom Array reporting metrics please define '
                'comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_srp', title='SRP',
            description='Collect Storage Resource Pool level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_srp_metrics', title='SRP Custom Metrics',
            description=(
                '(Optional) For custom SRP reporting metrics please define '
                'comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_sg', title='Storage Group',
            description='Collect Storage Group level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_sg_metrics', title='Storage Group Custom Metrics',
            description=(
                '(Optional) For custom SG reporting metrics please define '
                'comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_director', title='Director',
            description='Collect Director level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_fe_dir_metrics', title='FE Director Custom Metrics',
            description=(
                '(Optional) For custom FE Director reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_be_dir_metrics', title='BE Director Custom Metrics',
            description=(
                '(Optional) For custom BE Director reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_rdf_dir_metrics', title='RDF Director Custom Metrics',
            description=(
                '(Optional) For custom RDF Director reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_im_dir_metrics', title='IM Director Custom Metrics',
            description=(
                '(Optional) For custom IM Director reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_eds_dir_metrics', title='EDS Director Custom Metrics',
            description=(
                '(Optional) For custom EDS Director reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_em_dir_metrics', title='EM Director Custom Metrics',
            description=(
                '(Optional) For custom EM Director reporting metrics please '
                'define comma separated list of metrics here'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_port', title='Port',
            description='Collect Port level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_fe_port_metrics', title='FE Port Custom Metrics',
            description=(
                '(Optional) For custom FE Port reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_be_port_metrics', title='BE Port Custom Metrics',
            description=(
                '(Optional) For custom BE Port reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_rdf_port_metrics', title='RDF Port Custom Metrics',
            description=(
                '(Optional) For custom RDF Port reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_pg', title='Port Group',
            description='Collect Port Group level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_pg_metrics', title='Port Group Custom Metrics',
            description=(
                '(Optional) For custom Port Group reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_iscsi', title='iSCSI',
            description=(
                'Collect Endpoint(iSCSI Target) & IP Interface level information.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_ip_interface_metrics', title='IP Interface Custom Metrics',
            description=(
                '(Optional) For custom IP Interface reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_iscsi_target_metrics', title='Endpoint Custom Metrics',
            description=(
                '(Optional) For custom Endpoint reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_host', title='Host',
            description='Collect Host level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_host_metrics', title='Host Custom Metrics',
            description=(
                '(Optional) For custom Host reporting metrics please define '
                'comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_mv', title='Masking View',
            description='Collect Masking View level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_mv_metrics', title='Masking View Custom Metrics',
            description=(
                '(Optional) For custom Masking View reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_initiator', title='Initiator',
            description='Collect Initiator level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_initiator_metrics', title='Initiator Custom Metrics',
            description=(
                '(Optional) For custom Initiator reporting metrics please '
                'define comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_rdf', title='RDF Group',
            description='Collect RDF Group level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_rdfs_metrics', title='RDF/S Custom Metrics',
            description=(
                '(Optional) For custom RDF/S reporting metrics please define '
                'comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_rdfa_metrics', title='RDF/A Custom Metrics',
            description=(
                '(Optional) For custom RDF/A reporting metrics please define '
                'comma separated list of metrics here.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_metro_dr', title='Metro DR',
            description='Collect Metro Disaster Recovery level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_snap_policy', title='Snapshot Policy',
            description='Collect Snapshot Policy level information.',
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_audit_logs', title='Audit Logs',
            description=(
                'Collect system audit logs - WARNING: Only enable this once '
                'per instance of Unisphere configured with Splunk.'),
            required_on_create=False, required_on_edit=False))
        scheme.add_argument(smi.Argument(
            'select_alerts', title='Alerts',
            description=(
                'Collect Array alerts - WARNING: If Alerts are not managed '
                'in Unisphere this can result a significant level of data '
                'ingestion into Splunk.'),
            required_on_create=False, required_on_edit=False))
        return scheme

    def get_app_name(self):
        """Return the name of the add-on."""
        return 'TA-DellEMC_VMAX'

    def validate_input(self, definition):
        """Validate the input stanza."""
        input_module.validate_input(self, definition)

    def collect_events(self, ew):
        """Write out the events."""
        input_module.collect_events(self, ew)

    def get_account_fields(self):
        """Get any add-on account fields."""
        return list()

    def get_checkbox_fields(self):
        """Get any add-on checkbox fields."""
        checkbox_fields = list()
        checkbox_fields.append('enable_ssl')
        return checkbox_fields

    def get_global_checkbox_fields(self):
        """Get any add-on global checkbox fields"""
        if self.global_checkbox_fields is None:
            checkbox_name_file = os.path.join(
                bin_dir, 'global_checkbox_param.json')
            try:
                if os.path.isfile(checkbox_name_file):
                    with open(checkbox_name_file, 'r') as fp:
                        self.global_checkbox_fields = json.load(fp)
                else:
                    self.global_checkbox_fields = list()
            except Exception as e:
                self.log_error(
                    'Get exception when loading global checkbox parameter '
                    'names. ' + str(e))
                self.global_checkbox_fields = list()
        return self.global_checkbox_fields


if __name__ == "__main__":
    exitcode = ModInputinputs().run(sys.argv)
    sys.exit(exitcode)
