# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class NegociacionCRM(models.Model):
    _name = 'negociacion.crm'
    _description = 'Negociación CRM'

    @api.model
    def _getCategId(self):
        return [('categ_id', '=', self.env.ref('crm_vivicon.product_category_negociacion_crm').id)]

    lead_id = fields.Many2one(
        'crm.lead', 
        string='Oportunidad asociada', 
        required=True,
    )
    tipo_negociacion = fields.Many2one(
        'product.product', 
        string='Tipo de Negociación', 
        required=True,
        domain=_getCategId,
    )
    descripcion = fields.Char('Descripción', required=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id', readonly=True)
    monto = fields.Monetary(string='Monto', currency_field='company_currency', required=True, readonly=False)
