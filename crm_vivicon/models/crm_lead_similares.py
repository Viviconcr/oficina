# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class xCrmLeadSimilares(models.Model):
    _name = "xcrm.lead.similares"
    _description = 'Lead que tienen datos similares'

    lead_id = fields.Many2one(comodel_name='crm.lead', required=True,
                            auto_join=True,
                            ondelete='cascade', )
    lead_similar_id = fields.Many2one('crm.lead', string='Lead Similar', required=True, )
    nombre = fields.Char(related='lead_similar_id.name', )
    email_from = fields.Char(related='lead_similar_id.email_from', )
    telefono = fields.Char(related='lead_similar_id.mobile', )
    modelo_interes = fields.Many2many(related='lead_similar_id.modelo_interes', )