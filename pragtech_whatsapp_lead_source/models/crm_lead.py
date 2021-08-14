# -*- coding: utf-8 -*-
from odoo import fields, models, _
import logging
_logger = logging.getLogger(__name__)


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    chat_id = fields.Char('Chat Id')


