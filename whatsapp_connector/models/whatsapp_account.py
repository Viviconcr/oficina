# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

from odoo.exceptions import Warning, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class xWhatsapp(models.Model):
    _name = "xwhatsapp.account"
    _description = 'Whatsapp Account'
    # _rec_name = 'code'

    name = fields.Char(string="Name", required="True", help="Breve descripción para identificar la cuenta")
    phone = fields.Char(String="Phone", required="True", help="Número de teléfono de WhatsApp")
    whatsapp_endpoint = fields.Char(string="Whatsapp Endpoint", help="URL de la instancia en el Whatsapp api")
    whatsapp_token = fields.Char(string="Whatsapp Token")
    qr_code_image = fields.Binary(string="QR code")
    whatsapp_authenticate = fields.Boolean(string="Authenticate", default=False)
    active = fields.Boolean(string="Activo", default="True")

    def action_get_qr_code_source(self):
        # if not self.whatsapp_endpoint or not self.whatsapp_token:
        #     raise ValidationError('Debe haber ingresado el EndPoint y el token')
        return {
            'name': _("Scan WhatsApp QR Code"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'xwhatsapp.scan.qr.source',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_logout_from_whatsapp_source(self):        
        url = self.whatsapp_endpoint + '/logout?token=' + self.whatsapp_token

        headers = { "Content-Type": "application/json", }
        tmp_dict = { "accountStatus": "Logout request sent to WhatsApp" }
        response = requests.post(url, json.dumps(tmp_dict), headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            _logger.info("\nWhatsapp logout successfully")
            self.whatsapp_authenticate = False
