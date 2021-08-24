# -*- coding: utf-8 -*-

{
    'name': 'VIVICON - CRM Modifications',
    'category': 'Localization',
    'version': '1.0',
    'summary': 'CRM Modifications to adapt VIVICON needs',
    'description': """
    """,
    'author': 'Prointec S.A.',
    'depends': [
        'crm', 'stock', 
    ],
    'data':[
        'data/crm_metodos_pago_data.xml',
        'data/crm_stage_data.xml',
        'data/crm_vivicon_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        'views/stock_production_lot_views.xml',
        'views/crm_metodos_pago_views.xml',
        'views/crm_lead_views.xml',
        'views/menu_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}
