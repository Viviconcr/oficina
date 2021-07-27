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
    moneda = fields.Many2one("res.currency", string='Moneda', default=lambda self: self.env.ref('base.USD'))
    monto = fields.Monetary(string='Monto', currency_field='moneda', )
