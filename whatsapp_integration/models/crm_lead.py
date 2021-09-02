# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

from odoo.exceptions import Warning, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    x_chat_id = fields.Char(string="Chat Id", )
 

    def whatsapp_get_param(self):
        param = {'whatsapp_account_id': self.crm_project_id.whatsapp_account_id }
        param.update({'whatsapp_dest_phone': self.phone, 'whatsapp_chat_id': self.x_chat_id})
        return param
    
    def action_send_whatsapp_msg(self):
        # raise UserError('entro a la function')
        if not self.crm_project_id:
            raise ValidationError('El lead no tiene proyecto de interés')
        if not self.phone:
            raise ValidationError('El registro no tiene telefono o chat_id')
            return
        return {
            'name': _("Send Message on WhatsApp"),
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'xwhatsapp.msg.source',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
