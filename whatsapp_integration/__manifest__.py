# -*- coding: utf-8 -*-
{
    'name': 'Whatsapp Integration for CRM',
    'version': '14.0.0.1',
    'category': 'Extra Tools',
    'license': 'LGPL-3',    
    'author': 'Modify by Prointec',
    'website': "http://www.prointeccr.com",
    'summary': 'Whatsapp integration por odoo apps',
    'description': """
 Whatsapp Intregation for odoo apps.
    """,
    'depends': ['whatsapp_connector', 'crm', ],
    'data': [
        'data/utm_data.xml',
        'views/crm_lead_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
