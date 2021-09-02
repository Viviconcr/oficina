# -*- coding: utf-8 -*-
{
    'name': 'Whatsapp Connector',
    'version': '14.0.0.1',
    'category': 'Extra Tools',
    'license': 'LGPL-3',    
    'author': 'Modify by Prointec',
    'website': "http://www.prointeccr.com",
    'summary': 'Whatsapp connector by chat-api interface',
    'description': """
Whatsapp connector allow to odoo apps sending messagge by whatsapp.
    """,
    'depends': ['mail'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/whatsapp_scan_qr_views.xml',
        'wizard/whatsapp_send_msg.xml',
        'views/whatsapp_account_views.xml',
        'views/menu_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
