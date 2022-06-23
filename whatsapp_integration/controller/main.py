from odoo import http, models, api, _
import requests
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

import logging
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
            timezone = pytz.timezone(request.env['res.users'].sudo().browse([int(2)]).tz or 'UTC')
        dt = pytz.UTC.localize(date_time_obj)
        dt = dt.astimezone(timezone)
        dt = ustr(dt).split('+')[0]
        return date_time_obj

    # CallBack de whatsapp para lead
    @http.route(['/whatsapp/lead/source'], type='json', auth='public')
    def whatsapp_lead_response(self):
        _logger.info('>> whatsapp_integration.whatsapp_lead_response: Entering from webhook callback')
        data = json.loads(request.httprequest.data)
        _logger.info('>> whatsapp_integration.whatsapp_lead_response: webhook json: %s', data)
        if 'messages' in data and data['messages']:
            # msg_list = []
            # msg_dict = {}
            instance_id = data.get('instanceId')
            crm_lead_obj = request.env['crm.lead']
            whatsapp_obj = request.env['xwhatsapp.account']
            # crm_lead_id = ''

            waccount_id = None if not instance_id else whatsapp_obj.sudo().search([('instance_id','=', instance_id )], limit=1)

            if not waccount_id:
                _logger.info('>> whatsapp_integration.whatsapp_lead_response: No está registrada una cuenta de Whatsapp con instance_id : %s', instance_id )
                return

            carga_inicial_desde_utime = int(round(float(time.mktime(waccount_id.fecha_desde_carga_inicial.timetuple())), 0))


            # funcion que se usara más adelante
            busca_leads = lambda search_condition, search_order : crm_lead_obj.sudo().search(search_condition, order=search_order, limit=1)

            for msg in data['messages']:
                # _logger.info('>> whatsapp_integration.whatsapp_lead_response: msg: %s', msg)
                chat_id = msg.get('chatId')
                phone = "+" + re.split('[-@]', chat_id)[0]
                sender = str(msg.get('senderName', 'Cliente'))
                msg_utime = int(msg.get('time') or 0)

                parsed_phone = phonenumbers.parse(phone, 'CR')
                parsed_phone = phonenumbers.format_number( parsed_phone , phonenumbers.PhoneNumberFormat.INTERNATIONAL )
                # parsed_phone = "+" + str(parsed_phone.country_code) + " " + str(parsed_phone.national_number)[:4] + " " + str(parsed_phone.national_number)[4:]

                if msg.get('fromMe'):
                    # Mensajes enviados - desde el telefono o la app CRM(estos tienen un apostrofe al inicio)
                    if not ("`" in msg.get('body')[:4]):
                        # _logger.info('>> whatsapp_integration.whatsapp_lead_response: El mensaje es de FromMe: %s', msg.get('body'))
                        # el mensaje no generado por por el CRM, sino que fue ingresado directamente en el Whatsapp del teléfono
                        # TODO: Considerar si nay lead con igual numero o celular

                        crm_lead_id = busca_leads(['&', ('stage_id.sequence', '!=', 6), '|', ('phone', '=', parsed_phone), ('x_chat_id', '=', chat_id)], 'x_chat_id')
                        if not crm_lead_id:
                            crm_lead_id = busca_leads(['&', ('stage_id.sequence', '!=', 6), ('mobile', '=', parsed_phone)], 'mobile')
                        if crm_lead_id:
                            sender = request.env.user.name
                            crm_lead_id.message_post(
                                             body= ": " + str(msg.get('body')),
                                             subject= sender,
                                             message_type= 'notification',
                                             parent_id= False,
                                            )
                elif 'chatId' in msg and msg['chatId'] and not msg.get('fromMe'):
                    # _logger.info('>> whatsapp_integration.whatsapp_lead_response: El mensaje es NO es de FromMe: %s', phone)
                    
                    crm_lead_id = busca_leads(['&', ('stage_id.sequence', '!=', 6), '|', ('phone', '=', parsed_phone), ('x_chat_id', '=', chat_id)], 'x_chat_id')
                    if not crm_lead_id:
                        crm_lead_id = busca_leads(['&', ('stage_id.sequence', '!=', 6), ('mobile', '=', parsed_phone)], 'mobile')

                    if not crm_lead_id:
                        if msg_utime < carga_inicial_desde_utime:
                            continue
                        _logger.info('>> whatsapp_integration.whatsapp_lead_response: El mensaje NO es de FromMe y Debe crar un nuevo lead')
                        source_id = request.env.ref('whatsapp_integration.utm_source_whatsapp')
                        medium_id = request.env.ref('whatsapp_integration.utm_medium_whatsapp')
                        crm_lead_id = crm_lead_obj.sudo().create({
                                                                'name': msg.get('chatId'),
                                                                'phone': parsed_phone,
                                                                'x_chat_id': chat_id,
                                                                'type': 'opportunity',
                                                                'medium_id': medium_id.id,
                                                                'source_id': source_id.id,
                                                                'x_estado_mensaje': 'done'
                                                            })
                        email_template = request.env.ref('crm_vivicon.email_template_new_lead_whatsapp', False)
                        email_template.with_context(type='binary',
                                                    default_type='binary').send_mail(
                                                                            crm_lead_id.id,
                                                                            raise_exception=False,
                                                                            force_send=True)  # default_type='binary'
                    else:
                        # ya existe el lead
                        crm_lead_id.sudo().write( {'x_estado_mensaje': 'done'} )
                        _logger.info('>> whatsapp_integration.whatsapp_lead_response: Mensaje recibido en el lead: %s', crm_lead_id.id)
                    #Id del asesor al que esta asociado el lead, si no tuviera, se registra al usuario publico
                    notification_ids = [(0, 0, {
                        'res_partner_id': crm_lead_id.user_id.partner_id.id | request.env.ref('base.public_user').partner_id.id,
                        'notification_type': 'inbox'
                    })]
                    crm_lead_id.message_post(
                                     body= sender + ": " + str(msg.get('body')),
                                     subject= sender,
                                     message_type= 'notification',
                                     parent_id= False,
                                     notification_ids=notification_ids,
                                     subtype_id= request.env.ref("mail.mt_comment").id,
                                     author_id=request.env.ref('base.public_user').partner_id.id #se registra como autor al usuario publico
                    )
        return 'OK'
