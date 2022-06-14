# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

from odoo.exceptions import Warning, UserError, ValidationError
import requests
import json

import logging
_logger = logging.getLogger(__name__)

class xWhatsapp(models.Model):
    _name = "xwhatsapp.account"
    _description = 'Whatsapp Account'
    # _rec_name = 'code'

    name = fields.Char(string="Name", required="True", help="Breve descripción para identificar la cuenta")
    phone = fields.Char(string="Phone", required="True", help="Número de teléfono de WhatsApp")
    whatsapp_endpoint = fields.Char(string="Whatsapp Endpoint", help="URL de la instancia en el Whatsapp api")
    whatsapp_token = fields.Char(string="Whatsapp Token")
    qr_code_image = fields.Binary(string="QR code")
    whatsapp_authenticate = fields.Boolean(string="Authenticate", default=False)
    active = fields.Boolean(string="Activo", default="True")
    fecha_desde_carga_inicial = fields.Date(string="Fecha Inicial Cargas", required="True", help="Fecha desde la que se van a cargar nuevos mensajes")
    instance_id = fields.Char(string="Instance ID", store=True)


    def onchage_endpoint(self):
        if self.whatsapp_endpoint:
            self.whatsapp_endpoint = trim()
            if self.whatsapp_endpoint[len(self.whatsapp_endpoint)-1]=='/':
                self.whatsapp_endpoint = self.whatsapp_endpoint[:len(self.whatsapp_endpoint)-1]
        
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

    @api.onchange('whatsapp_endpoint')
    def onchange_whatsapp_endpoint(self):
        if self.whatsapp_endpoint:
            self.instance_id = self.whatsapp_endpoint[self.whatsapp_endpoint.find('instance')+8:]

    def action_logout_from_whatsapp_source(self):        
        url = self.whatsapp_endpoint + '/logout?token=' + self.whatsapp_token

        headers = { "Content-Type": "application/json", }
        tmp_dict = { "accountStatus": "Logout request sent to WhatsApp" }
        response = requests.post(url, json.dumps(tmp_dict), headers=headers)
        if response.status_code == 201 or response.status_code == 200:
            _logger.info("\nWhatsapp logout successfully")
            self.whatsapp_authenticate = False

    def whatsapp_get_param(self):
        param = {'whatsapp_account_id': self.id, 'whatsapp_chat_id': None}
        try:
            emp = self.env['hr.employee'].search([('user_id', '=', self.env.uid), ('company_id', '=', self.env.company.id)], limit=1)
            if emp:
                param.update({'whatsapp_dest_phone': emp.mobile_phone})
        except Exception:
            # Ignora el error que se supone es porque no esta instalado el módulo de empleados
            pass
        return param

    def action_send_test_msg(self):
        # raise UserError('entro a la function:  action_test_send_msg')
        if not self.phone:
            raise ValidationError('El registro no tiene telefono o chat_id')
            return
        param = self.whatsapp_get_param()
        ctx = {'default_test_mode': True, 'default_dest_phone': param.get('whatsapp_dest_phone'), }
        return {
            'name': _("Send Message on WhatsApp"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'xwhatsapp.msg.source',
            'type': 'ir.actions.act_window',
            'context': ctx,
            'target': 'new',
        }
