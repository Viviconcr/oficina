# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

from odoo.exceptions import Warning, UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class xCrmProjects(models.Model):
    _name = "xcrm.projects"
    _description = 'CRM Projects'
    # _rec_name = 'code'

    code = fields.Char(String="Código", required="True", help="Código del Proyecto")
    name = fields.Char(string="Nombre", required="True", help="Nombre del Proyecto")
    whatsapp_account_id = fields.Many2one('xwhatsapp.account', string='Cuenta WhatsApp')
    active = fields.Boolean(string="Activo", default="True")