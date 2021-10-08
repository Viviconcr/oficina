# -*- coding: utf-8 -*-
from __future__ import print_function
import functools
import traceback
import sys

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from datetime import timedelta, datetime
import logging
_logger = logging.getLogger(__name__)


class CrmLeadLost(models.TransientModel):
    _inherit = 'crm.lead.lost'

    x_lost_detail = fields.Char(string='Detalle', help='Detalle de la perdida')

    def action_lost_reason_apply(self):
        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        return leads.action_set_lost(lost_reason=self.lost_reason_id.id,x_lost_detail=self.x_lost_detail)
