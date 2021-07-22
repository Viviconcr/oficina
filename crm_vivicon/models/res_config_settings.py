# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_aprobar_negociaciones = fields.Boolean(string="Puede aprobar negociaciones", implied_group='crm_vivicon.group_aprobar_negociaciones')
