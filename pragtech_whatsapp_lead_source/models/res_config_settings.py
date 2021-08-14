import logging
import requests
import base64
import json
_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class base(models.TransientModel):
    _inherit = "res.config.settings"

    whatsapp_endpoint_for_lead = fields.Char('Whatsapp Endpoint', help="Whatsapp api endpoint url with instance id")
    whatsapp_token_for_lead = fields.Char('Whatsapp Token')
    qr_code_image_for_lead = fields.Binary("QR code")
    whatsapp_authenticate_for_lead = fields.Boolean('Authenticate', default=False)

    @api.model
    def get_values(self):
        res = super(base, self).get_values()
        Param = self.env['ir.config_parameter'].sudo()
        res['whatsapp_endpoint_for_lead'] = Param.sudo().get_param('pragtech_whatsapp_lead_source.whatsapp_endpoint_for_lead')
        res['whatsapp_token_for_lead'] = Param.sudo().get_param('pragtech_whatsapp_lead_source.whatsapp_token_for_lead')
        res['whatsapp_authenticate_for_lead'] = Param.sudo().get_param('pragtech_whatsapp_lead_source.whatsapp_authenticate_for_lead')
        res.update(qr_code_image_for_lead=Param.sudo().get_param('pragtech_whatsapp_lead_source.qr_code_image_for_lead'))
        return res

    def set_values(self):
        super(base, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_lead_source.whatsapp_endpoint_for_lead', self.whatsapp_endpoint_for_lead)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_lead_source.whatsapp_token_for_lead', self.whatsapp_token_for_lead)
        self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_lead_source.qr_code_image_for_lead', self.qr_code_image_for_lead)

    def action_get_qr_code_lead_source(self):
        return {
            'name': _("Scan WhatsApp QR Code"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'whatsapp.scan.qr.lead.source',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def action_logout_from_whatsapp_lead_source(self):
        Param = self.sudo().get_values()
        url = Param.get('whatsapp_endpoint_for_lead') + '/logout?token=' + Param.get('whatsapp_token_for_lead')
        headers = {
            "Content-Type": "application/json",
        }
        tmp_dict = {
            "accountStatus": "Logout request sent to WhatsApp"
        }
        response = requests.post(url, json.dumps(tmp_dict), headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            _logger.info("\nWhatsapp logout successfully")
            self.env['ir.config_parameter'].sudo().set_param('pragtech_whatsapp_lead_source.whatsapp_authenticate_for_lead', False)
