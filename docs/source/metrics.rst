Unisphere for PowerMax Performance Metrics
==========================================
The PowerMax for Splunk TA ingests a wide range of metrics across each of the
reporting levels. To get detailed definitions of each please consult the
official Unisphere for PowerMax documentation available through the Unisphere
UI in ``Help Options > Online Help``.

When in the official documentation performance metrics can be found in the
section ``Performance Management > Performance Management Metrics.`` From there
you can select the performance category you want to see available metrics for.

Unfortunately this list does not provide users with the format required for
each of these performance categories when querying for data via REST. To assist
with this process there is a list of REST API valid metrics available in the
various performance category links below. Tables within contain the each
supported metric in the ``CamelCase`` format required for Unisphere (& custom
metrics list), the formatted ``snake_case`` metric as seen in Splunk, and if
the metric is a KPI or not.

.. note::
    Whilst the Unisphere metrics are all in ``CamelCase`` format, the PowerMax
    for Splunk TA will convert them all to ``snake_case`` so all keys in Splunk
    PowerMax events have consistent formatting.

.. note::
    When defining custom lists of metrics for a given performance category
    in PowerMax for Splunk data input configuration, metrics **must** be in
    ``CamelCase`` format. These are required for the REST requests to the
    Unisphere REST API, the conversion to ``snake_case`` happens after this
    data has been retrieved.

..  toctree::
    :maxdepth: 2

    metrics/array
    metrics/srp
    metrics/storage_group
    metrics/fe_dir
    metrics/be_dir
    metrics/rdf_dir
    metrics/im_dir
    metrics/eds_dir
    metrics/fe_port
    metrics/be_port
    metrics/rdf_port
    metrics/host
    metrics/initiator
    metrics/port_group
    metrics/masking_view
    metrics/ip_interface
    metrics/iscsi_target
    metrics/rdfa
    metrics/rdfs
