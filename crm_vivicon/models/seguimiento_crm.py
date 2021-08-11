# -*- coding: utf-8 -*-

from odoo import models, fields, _

class SeguimientoCRM(models.Model):
    _name = 'seguimiento.crm'
    _description = 'Detalle Seguimiento CRM'

    lead_id = fields.Many2one(
        'crm.lead', 
        string='Oportunidad asociada', 
        required=True,
    )    

    fecha = fields.Date(string='Fecha', required=True)
    detalle = fields.Char('Detalle', required=True)
