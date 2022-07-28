# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class xUtmCampaign(models.Model):
    _inherit = 'utm.campaign'

    whatsapp_account_id = fields.Many2one('xwhatsapp.account', string='Cuenta WhatsApp')


