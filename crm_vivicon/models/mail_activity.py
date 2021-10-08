# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging
import pytz

from odoo import api, exceptions, fields, models, _

_logger = logging.getLogger(__name__)


class MailActivityType(models.Model):
    _inherit = 'mail.activity'

    def action_notify(self):
        return