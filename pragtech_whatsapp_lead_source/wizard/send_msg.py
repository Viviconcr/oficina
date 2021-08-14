# -*- coding: utf-8 -*-
import logging
import json
import requests
from odoo import api, fields, models, _ , tools
from odoo.exceptions import Warning
from odoo.exceptions import UserError
import base64
import time
import re
import uuid
from odoo.tools import groupby, formataddr

_logger = logging.getLogger(__name__)
try:
    import phonenumbers
    from phonenumbers.phonenumberutil import region_code_for_country_code
    _sms_phonenumbers_lib_imported = True

except ImportError:
    _sms_phonenumbers_lib_imported = False
    _logger.info(
        "The `phonenumbers` Python module is not available. "
        "Phone number validation will be skipped. "
        "Try `pip3 install phonenumbers` to install it."
    )

class ScanWAQRCode(models.TransientModel):
    _name = 'whatsapp.scan.qr.lead.source'
    _description = 'Scan WhatsApp QR Code'

    def _get_default_image(self):

        Param = self.env['res.config.settings'].sudo().get_values()
        Param_set = self.env['ir.config_parameter'].sudo()
        url = Param.get('whatsapp_endpoint_for_lead') + '/status?token=' + Param.get('whatsapp_token_for_lead')
        response = requests.get(url)
        json_response = json.loads(response.text)

        if (response.status_code == 201 or response.status_code == 200) and (json_response['accountStatus'] == 'got qr code'):
            # qr_code_image
            qr_code_url = Param.get('whatsapp_endpoint_for_lead') + '/qr_code?token=' + Param.get('whatsapp_token_for_lead')
            response_qr_code = requests.get(qr_code_url)
            img = base64.b64encode(response_qr_code.content)
            Param_set.set_param("pragtech_whatsapp_lead_source.whatsapp_authenticate_for_lead", True)
            return img

    qr_code_img_data_for_lead= fields.Binary(default=_get_default_image)

