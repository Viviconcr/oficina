# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class crmMetodosPago(models.Model):
    _name = "crm.metodos.pago"
    _description = 'Métodos de Pago CRM'

    name = fields.Char(string="Nombre", size=100, required=True, )
    active = fields.Boolean(string="Activo", required=True, default=True)
