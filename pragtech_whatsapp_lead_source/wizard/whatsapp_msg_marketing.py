import requests
import json
import datetime
from odoo.exceptions import UserError
from odoo import api, fields, models, _ , tools
import logging
import phonenumbers
_logger = logging.getLogger(__name__)


class SendWAMessageMarketing(models.TransientModel):
    _name = 'whatsapp.msg.lead.source'
    _description = 'Send WhatsApp Message'
    _inherit =  ['mail.thread', 'mail.activity.mixin']

    def _default_unique_user(self):
        IPC = self.env['ir.config_parameter'].sudo()
        dbuuid = IPC.get_param('database.uuid')
        return dbuuid + '_' + str(self.env.uid)

    message = fields.Text('Message', required=True)
    attachment_ids = fields.Many2many(
        'ir.attachment', 'whatsapp_msg_marketing_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    unique_user = fields.Char(default=_default_unique_user)

    @api.model
    def default_get(self, fields):
        result = super(SendWAMessageMarketing, self).default_get(fields)
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        return result

    def action_send_msg_marketing(self):
        active_model = self.env.context.get('active_model')
        res_id = self.env.context.get('active_id')
        rec = self.env[active_model].browse(res_id)
        param = self.env['res.config.settings'].sudo().get_values()
        status_url = param.get('whatsapp_endpoint_for_lead') + '/status?token=' + param.get('whatsapp_token_for_lead')
        status_response = requests.get(status_url)
        json_response_status = json.loads(status_response.text)

        parsed_phone = phonenumbers.parse(rec.phone, 'CR')
        _logger.error("MAB - \n Parsed phone: %s", parsed_phone)
        parsed_phone = str(parsed_phone.country_code) + str(parsed_phone.national_number)
        sender = self.env.user.name
        
        if (status_response.status_code == 200 or status_response.status_code == 201) and json_response_status[
            'accountStatus'] == 'authenticated':
            if active_model == 'crm.lead':
                url = param.get('whatsapp_endpoint_for_lead') + '/sendMessage?token=' + param.get('whatsapp_token_for_lead')
                headers = {
                    "Content-Type": "application/json",
                }
                if rec.chat_id:
                    tmp_dict = {
                        "chatId": str(rec.chat_id),
                        "body": self.message}
                else:
                    tmp_dict = {
                        "phone": parsed_phone,
                        "body": self.message}

                response = requests.post(url, json.dumps(tmp_dict), headers=headers)
                if response.status_code == 201 or response.status_code == 200:
                    #rec.message_post(
                    #    body= sender + ": " + self.message,
                    #    subject= sender,
                    #    message_type= 'notification',
                    #    parent_id= False,
                    #    attachments=self.attachment_ids,
                    #)
                    _logger.error("\nSend Message to contact successfully \n dict: %s", tmp_dict)
                if self.attachment_ids:
                    for attachment in self.attachment_ids:
                        with open("/tmp/" + attachment.name, 'wb') as tmp:
                            encoded_file = str(attachment.datas)
                            url_send_file = param.get('whatsapp_endpoint_for_lead') + '/sendFile?token=' + param.get(
                                'whatsapp_token_for_lead')
                            headers_send_file = {
                                "Content-Type": "application/json",
                            }
                            if rec.chat_id:
                                dict_send_file = {
                                    "chatId": str(rec.chat_id),
                                    "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                    "filename": attachment.name
                                }
                            else:
                                dict_send_file = {
                                    "phone": parsed_phone,
                                    "body": "data:" + attachment.mimetype + ";base64," + encoded_file[2:-1],
                                    "filename": attachment.name
                                }

                            response_send_file = requests.post(url_send_file, json.dumps(dict_send_file),
                                                               headers=headers_send_file)
                            if response_send_file.status_code == 201 or response_send_file.status_code == 200:
                                _logger.info("\nSend file attachment successfully!!")

        else:
            raise UserError(_('Please authorize your mobile number with chat api'))
