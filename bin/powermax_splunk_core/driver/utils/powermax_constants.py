"""bin/powermax_splunk_core/driver/utils/powermax_constants.py"""

VERSION = 3.0

# Inputs.conf keys
INPUT_KEY = 'input_key'
OFF = 'off'
ON = 'on'
KPI = 'kpi'
ALL = 'all'
CUSTOM = 'custom'
METRICS = 'custom_metric'
U4P_CAT = 'unisphere_performance_category'
ARRAY = 'array'
SRP = 'srp'
STORAGE_GROUP = 'storage_group'
DIRECTOR = 'director'
PORT = 'port'
PORT_GROUP = 'port_group'
HOST = 'host'
INITIATOR = 'initiator'
MASKING_VIEW = 'masking_view'
ISCSI = 'iscsi'
RDF = 'rdf'
METRO_DR = 'metro_dr'
SNAP_POLICY = 'snap_policy'
ALERTS = 'alerts'
AUDIT_LOGS = 'audit_logs'
FE_DIRECTOR = 'fe_director'
BE_DIRECTOR = 'be_director'
RDF_DIRECTOR = 'rdf_director'
IM_DIRECTOR = 'im_director'
EDS_DIRECTOR = 'eds_director'
EM_DIRECTOR = 'em_director'
FE_PORT = 'fe_port'
BE_PORT = 'be_port'
RDF_PORT = 'rdf_port'
ISCSI_TARGET = 'iscsi_target'
IP_INTERFACE = 'ip_interface'
RDFS = 'rdfs'
RDFA = 'rdfa'

REPORTING_LEVELS = [
    ARRAY, SRP, STORAGE_GROUP, DIRECTOR, PORT, PORT_GROUP, ISCSI, HOST,
    INITIATOR, MASKING_VIEW, RDF, METRO_DR, SNAP_POLICY, ALERTS, AUDIT_LOGS
]

# Inputs.conf key mapping
REPORTING_LEVELS_KEY_MAP = {
    ARRAY: 'select_array',
    SRP: 'select_srp',
    STORAGE_GROUP: 'select_sg',
    DIRECTOR: 'select_director',
    PORT: 'select_port',
    PORT_GROUP: 'select_pg',
    ISCSI: 'select_iscsi',
    HOST: 'select_host',
    INITIATOR: 'select_initiator',
    MASKING_VIEW: 'select_mv',
    RDF: 'select_rdf',
    METRO_DR: 'select_metro_dr',
    SNAP_POLICY: 'select_snap_policy',
    ALERTS: 'select_alerts',
    AUDIT_LOGS: 'select_audit_logs',
}

PERFORMANCE_CATEGORIES = [
    ARRAY, SRP, STORAGE_GROUP, FE_DIRECTOR, BE_DIRECTOR, RDF_DIRECTOR,
    IM_DIRECTOR, EDS_DIRECTOR, EM_DIRECTOR, FE_PORT, BE_PORT, RDF_PORT,
    PORT_GROUP, HOST, INITIATOR, MASKING_VIEW, ISCSI_TARGET, IP_INTERFACE,
    RDFS, RDFA
]

# Inputs.conf key mapping
PERFORMANCE_KEY_MAP = {
    ARRAY: {
        INPUT_KEY: 'select_array', OFF: 'array_off', KPI: 'array_kpi',
        ALL: 'array_all', CUSTOM: 'array_custom', U4P_CAT: 'Array',
        METRICS: 'select_array_metrics'},
    SRP: {
        INPUT_KEY: 'select_srp', OFF: 'srp_off', KPI: 'srp_kpi',
        ALL: 'srp_all', CUSTOM: 'srp_custom', U4P_CAT: 'SRP',
        METRICS: 'select_srp_metrics'},
    STORAGE_GROUP: {
        INPUT_KEY: 'select_sg', OFF: 'sg_off', KPI: 'sg_kpi',
        ALL: 'sg_all', CUSTOM: 'sg_custom', U4P_CAT: 'StorageGroup',
        METRICS: 'select_sg_metrics'},
    FE_DIRECTOR: {
        INPUT_KEY: 'select_director', OFF: 'dir_off', KPI: 'dir_kpi',
        ALL: 'dir_all', CUSTOM: 'dir_custom', U4P_CAT: 'FEDirector',
        METRICS: 'select_fe_dir_metrics'},
    BE_DIRECTOR: {
        INPUT_KEY: 'select_director', OFF: 'dir_off', KPI: 'dir_kpi',
        ALL: 'dir_all', CUSTOM: 'dir_custom', U4P_CAT: 'BEDirector',
        METRICS: 'select_be_dir_metrics'},
    RDF_DIRECTOR: {
        INPUT_KEY: 'select_director', OFF: 'dir_off', KPI: 'dir_kpi',
        ALL: 'dir_all', CUSTOM: 'dir_custom', U4P_CAT: 'RDFDirector',
        METRICS: 'select_rdf_dir_metrics'},
    IM_DIRECTOR: {
        INPUT_KEY: 'select_director', OFF: 'dir_off', KPI: 'dir_kpi',
        ALL: 'dir_all', CUSTOM: 'dir_custom', U4P_CAT: 'IMDirector',
        METRICS: 'select_im_dir_metrics'},
    EDS_DIRECTOR: {
        INPUT_KEY: 'select_director', OFF: 'dir_off', KPI: 'dir_kpi',
        ALL: 'dir_all', CUSTOM: 'dir_custom', U4P_CAT: 'EDSDirector',
        METRICS: 'select_eds_dir_metrics'},
    EM_DIRECTOR: {
        INPUT_KEY: 'select_director', OFF: 'dir_off', KPI: 'dir_kpi',
        ALL: 'dir_all', CUSTOM: 'dir_custom', U4P_CAT: 'EMDirector',
        METRICS: 'select_em_dir_metrics'},
    FE_PORT: {
        INPUT_KEY: 'select_port', OFF: 'port_off', KPI: 'port_kpi',
        ALL: 'port_all', CUSTOM: 'port_custom', U4P_CAT: 'FEPort',
        METRICS: 'select_fe_port_metrics'},
    BE_PORT: {
        INPUT_KEY: 'select_port', OFF: 'port_off', KPI: 'port_kpi',
        ALL: 'port_all', CUSTOM: 'port_custom', U4P_CAT: 'BEPort',
        METRICS: 'select_be_port_metrics'},
    RDF_PORT: {
        INPUT_KEY: 'select_port', OFF: 'port_off', KPI: 'port_kpi',
        ALL: 'port_all', CUSTOM: 'port_custom', U4P_CAT: 'RDFPort',
        METRICS: 'select_rdf_port_metrics'},
    PORT_GROUP: {
        INPUT_KEY: 'select_pg', OFF: 'pg_off', KPI: 'pg_kpi',
        ALL: 'pg_all', CUSTOM: 'pg_custom', U4P_CAT: 'PortGroup',
        METRICS: 'select_pg_metrics'},
    ISCSI_TARGET: {
        INPUT_KEY: 'select_iscsi', OFF: 'iscsi_off', KPI: 'iscsi_kpi',
        ALL: 'iscsi_all', CUSTOM: 'iscsi_custom', U4P_CAT: 'ISCSITarget',
        METRICS: 'select_iscsi_target_metrics'},
    IP_INTERFACE: {
        INPUT_KEY: 'select_iscsi', OFF: 'iscsi_off', KPI: 'iscsi_kpi',
        ALL: 'iscsi_all', CUSTOM: 'iscsi_custom', U4P_CAT: 'IPInterface',
        METRICS: 'select_ip_interface_metrics'},
    HOST: {
        INPUT_KEY: 'select_host', OFF: 'host_off', KPI: 'host_kpi',
        ALL: 'host_all', CUSTOM: 'host_custom', U4P_CAT: 'Host',
        METRICS: 'select_host_metrics'},
    INITIATOR: {
        INPUT_KEY: 'select_initiator', OFF: 'init_off', KPI: 'init_kpi',
        ALL: 'init_all', CUSTOM: 'init_custom', U4P_CAT: 'Initiator',
        METRICS: 'select_initiator_metrics'},
    MASKING_VIEW: {
        INPUT_KEY: 'select_mv', OFF: 'mv_off', KPI: 'mv_kpi',
        ALL: 'mv_all', CUSTOM: 'mv_custom', U4P_CAT: 'MaskingView',
        METRICS: 'select_mv_metrics'},
    RDFS: {
        INPUT_KEY: 'select_rdf', OFF: 'rdf_off', KPI: 'rdf_kpi',
        ALL: 'rdf_all', CUSTOM: 'rdf_custom', U4P_CAT: 'RDFS',
        METRICS: 'select_rdfs_metrics'},
    RDFA: {
        INPUT_KEY: 'select_rdf', OFF: 'rdf_off', KPI: 'rdf_kpi',
        ALL: 'rdf_all', CUSTOM: 'rdf_custom', U4P_CAT: 'RDFA',
        METRICS: 'select_rdfa_metrics'},
}
