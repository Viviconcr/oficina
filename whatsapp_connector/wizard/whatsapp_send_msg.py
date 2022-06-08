from odoo import api, fields, models, _ , tools
from odoo.exceptions import Warning, UserError, ValidationError

import json
import requests
import datetime
import phonenumbers
import base64

import logging
_logger = logging.getLogger(__name__)


class SendWAMessageMarketing(models.TransientModel):
    _name = 'xwhatsapp.msg.source'
    _description = 'Send WhatsApp Message'
    _inherit =  ['mail.thread', 'mail.activity.mixin']

    def _default_unique_user(self):
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        return dbuuid + '_' + str(self.env.uid)


    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many('ir.attachment', 'xwhatsapp_msg_source_ir_attachments_rel',
                                        'wizard_id', 'attachment_id', 'Attachments')
    unique_user = fields.Char(default=_default_unique_user)
    test_mode = fields.Boolean(string='test mode', default=False)
    dest_phone = fields.Char(string='Celular Destino')


    @api.model
    def default_get(self, fields):
        result = super(SendWAMessageMarketing, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        if self.env.context.get('default_test_mode', False):
            result.update({'test_mode': True})
        return result

    def action_send_msg(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if not self.test_mode and not self.dest_phone:
            raise UserError('Debe indicar el número de teléfono destino del mensaje')
        if not active_model or not active_id:
            raise UserError('action_send_msg: No se pudo obtener el "active_model" or el registro actual' )            
        rec = self.env[active_model].browse( active_id )

        wparam = rec.whatsapp_get_param()

        wchat_id = wparam.get('whatsapp_chat_id')
        waccount_id = wparam.get('whatsapp_account_id')
        dest_phone = self.dest_phone or wparam.get('whatsapp_dest_phone')

        if not waccount_id:
            raise UserError('action_send_msg: No recibió las variables de contexto "whatsapp_account_id" ')
        elif not dest_phone:
            raise UserError('action_send_msg: No recibió la variable de contexto "whatsapp_dest_phone" ')

        _logger.info('>> whatsapp_send_msg.action_send_msg: account_id %s ', waccount_id)
        waccount = self.env['xwhatsapp.account'].browse(waccount_id)

        _logger.info('>> whatsapp_send_msg.action_send_msg: waccount %s ', str(waccount))
        status_url = waccount.whatsapp_endpoint + '/status?token=' + waccount.whatsapp_token
        _logger.info('>> whatsapp_send_msg.action_send_msg: account %s,  URL: %s', str(waccount), status_url)
    
        status_response = requests.get(status_url)
        _logger.info(">> whatsapp_send_msg.action_send_msg: - \n status_response: %s", str(status_response))
        json_response_status = json.loads(status_response.text)

        parsed_phone = phonenumbers.parse(dest_phone, 'CR')
        _logger.info(">> whatsapp_send_msg.action_send_msg: - \n Parsed phone: %s", parsed_phone)
        parsed_phone = str(parsed_phone.country_code) + str(parsed_phone.national_number)
        sender = self.env.user.name

        if ((status_response.status_code == 200 or status_response.status_code == 201) and json_response_status['accountStatus'] == 'authenticated' ):

            url = waccount.whatsapp_endpoint + '/sendMessage?token=' + waccount.whatsapp_token
            headers = { "Content-Type": "application/json", }

            tmp_dict = { "chatId": str(wchat_id) } if wchat_id else { "phone": parsed_phone }
            tmp_dict.update( {"body": self.message} )

            response = requests.post(url, json.dumps(tmp_dict), headers=headers)
            
            # El mensaje se coloca en el chatter y se le agrega el inicio el caracter ` para que el controller
            # no los agregue tambien 
            if response.status_code == 201 or response.status_code == 200:
                attachments = []
                for attachment in self.attachment_ids:
                    attachments.append( ['wm'+str(attachment.id)+'_'+attachment.name, base64.b64decode(attachment.datas)] )
                if not self.test_mode:
                    # suponemos que quien hace en envio, tiene  chatter
                    rec.message_post(body= "`" + sender + ": " + self.message,
                                    subject= sender, message_type='notification', parent_id=False, attachments=attachments, )
                # rec.sudo().write( {'x_estado_mensaje': 'normal'} )

            if self.attachment_ids:
                for attachment in self.attachment_ids:
                    with open("/tmp/" + attachment.name, 'wb') as tmp:
                        encoded_file = str(attachment.datas)
                        url_send_file = waccount.whatsapp_endpoint + '/sendFile?token=' + waccount.whatsapp_token
                        headers_send_file = { "Content-Type": "application/json", }

                        dict_send_file = { "chatId": str(wchat_id) } if wchat_id else { "phone": parsed_phone }
                        dict_send_file.update( {"body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1], "filename": attachment.name} )

                        response_send_file = requests.post(url_send_file, json.dumps(dict_send_file), headers=headers_send_file)
                        if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                            _logger.info(">> whatsapp_send_msg.action_send_msg: \nSend file attachment successfully!!")
        else:
            raise UserError(_('Please authorize your mobile number with chat api. response data:') + str(status_response) )