# -*- coding: utf-8 -*-
from odoo import api, fields, models, _ , tools
from odoo.exceptions import Warning, UserError, ValidationError

import json
import requests
import base64
import time
import re
import uuid
from odoo.tools import groupby, formataddr

import logging
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
    _name = 'xwhatsapp.scan.qr.source'
    _description = 'Scan WhatsApp QR Code'

    def _get_default_image(self):
        active_id = self.env.context.get('active_id')   # ID de la cuenta de Whatsapp
        if not active_id:
            raise UserError('No hay ningún registro activo')
        waccount = self.env['xwhatsapp.account'].browse(active_id)
        if not waccount.whatsapp_endpoint or not waccount.whatsapp_token:
            raise UserError('La cuenta no tiene ingresada el EndPoint o el token')
        
        url = waccount.whatsapp_endpoint + '/status?token=' + waccount.whatsapp_token
        response = requests.get(url)
        json_response = json.loads(response.text)
        
        if (response.status_code == 201 or response.status_code == 200) and (json_response['accountStatus'] == 'got qr code'):
            # qr_code_image
            qr_code_url = waccount.whatsapp_endpoint + '/qr_code?token=' + waccount.whatsapp_token
            response_qr_code = requests.get(qr_code_url)
            img = base64.b64encode(response_qr_code.content)
            waccount.whatsapp_authenticate = True
            return img

    qr_code_img_data = fields.Binary(default=_get_default_image)
