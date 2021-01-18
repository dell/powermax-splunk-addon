"""bin/TA_DellEMC_VMAX_rh_settings.py"""

import ta_dellemc_vmax_declare # NOQA

from splunk_aoblib.rest_migration import ConfigMigrationHandler

from splunktaucclib.rest_handler.endpoint import field
from splunktaucclib.rest_handler.endpoint import MultipleModel
from splunktaucclib.rest_handler.endpoint import RestModel

from splunktaucclib.rest_handler import admin_external
from splunktaucclib.rest_handler import util

util.remove_http_proxy_env_vars()

fields_logging = [
    field.RestField(
        'loglevel',
        required=False,
        encrypted=False,
        default='INFO',
        validator=None
    )
]
model_logging = RestModel(fields_logging, name='logging')

endpoint = MultipleModel(
    'ta_dellemc_vmax_settings',
    models=[
        model_logging
    ],
)

if __name__ == '__main__':
    admin_external.handle(
        endpoint,
        handler=ConfigMigrationHandler,
    )
