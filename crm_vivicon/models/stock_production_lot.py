# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

from odoo.exceptions import Warning, UserError, ValidationError

_logger = logging.getLogger(__name__)


class VivStockproductionLot(models.Model):
    _inherit = 'stock.production.lot'

    x_area_lote = fields.Float(string="Área Lote")
    x_area_construcion = fields.Float(string="Área construcción")
    x_folio_real = fields.Char(string="Folio Real", copy=False)
    x_numero_plano = fields.Char(string="Número de Plano", copy=False)
