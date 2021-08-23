import requests
from odoo import http, _, models, api
import logging
import json
from odoo.exceptions import UserError
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.http import request
import phonenumbers
import datetime
import time
import pytz
import re
from odoo.tools import ustr

import base64

_logger = logging.getLogger(__name__)


class AuthSignupHomeDerived(AuthSignupHome):

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""
        get_param = request.env['ir.config_parameter'].sudo().get_param
        countries = request.env['res.country'].sudo().search([])
        return {
            'signup_enabled': request.env['res.users']._get_signup_invitation_scope() == 'b2c',
            'reset_password_enabled': get_param('auth_signup.reset_password') == 'True',
            'countries': countries
        }

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = {key: qcontext.get(key) for key in ('login', 'name', 'password', 'mobile', 'country_id')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_langs = [lang['code'] for lang in request.env['res.lang'].sudo().search_read([], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()


class Whatsapp(http.Controller):

    def convert_epoch_to_unix_timestamp(self, msg_time):
        formatted_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg_time))
        date_time_obj = datetime.datetime.strptime(formatted_time, '%Y-%m-%d %H:%M:%S')
        dt = False
        if date_time_obj:
            timezone = pytz.timezone(request.env['res.users'].
                                     sudo().browse([int(2)]).tz or 'UTC')
        dt = pytz.UTC.localize(date_time_obj)
        dt = dt.astimezone(timezone)
        dt = ustr(dt).split('+')[0]
        return date_time_obj

    @http.route(['/whatsapp/lead/source'], type='json', auth='public')
    def whatsapp_responce(self):
        _logger.error('MAB - Entering webhook')
        data = json.loads(request.httprequest.data)
        _logger.error('MAB - webhook json: %s', data)
        if 'messages' in data and data['messages']:
            msg_list = []
            msg_dict = {}
            crm_lead_obj = request.env['crm.lead']
            crm_lead_id = ''

            for msg in data['messages']:
                _logger.error('MAB - webhook msg: %s', msg)
                chat_id = msg.get('chatId')
                phone = "+" + re.split('[-@]', chat_id)[0]
                sender = str(msg.get('senderName', 'Cliente'))
                
                if msg.get('fromMe'):
                    crm_lead_id = crm_lead_obj.sudo().search(['|', '|', ('phone', '=', phone), ('mobile', '=', phone), ('chat_id', '=', chat_id)], limit=1)
                    if crm_lead_id:
                        sender = request.env.user.name
                        crm_lead_id.message_post(
                                         body= sender + ": " + str(msg.get('body')),
                                         subject= sender,
                                         message_type= 'notification',
                                         parent_id= False,
                        )
                elif 'chatId' in msg and msg['chatId'] and not msg.get('fromMe'):
                    parsed_phone = phonenumbers.parse(phone, 'CR')
                    parsed_phone = "+" + str(parsed_phone.country_code) + " " + str(parsed_phone.national_number)
                    crm_lead_id = crm_lead_obj.sudo().search(['&', ('stage_id.sequence', '!=', 6),
                                                                   '|', '|', ('chat_id', '=', chat_id), ('phone', '=', parsed_phone), 
                                                                        ('mobile', '=', parsed_phone)], limit=1)
                    if not crm_lead_id:
                        source_id = request.env.ref('pragtech_whatsapp_lead_source.utm_source_whatsapp')
                        medium_id = request.env.ref('pragtech_whatsapp_lead_source.utm_medium_whatsapp')

                        crm_lead_id = crm_lead_obj.sudo().create({
                            'name': msg.get('chatId'),
                            'phone': parsed_phone,
                            'chat_id': chat_id,
                            'type': 'opportunity',
                            'medium_id': medium_id.id,
                            'source_id': source_id.id,
                        })
                        #crm_lead_id.description = "Customer: " + str(msg.get('body'))
                    crm_lead_id.message_post(
                                     body= sender + ": " + str(msg.get('body')),
                                     subject= sender,
                                     message_type= 'notification',
                                     parent_id= False,
                    )
                    #_logger.error('MAB - update lead description v2: %s', crm_lead_id.description)
        return 'OK'
