
{
    'name': 'VIVICON - CRM Modifications',
    'category': 'Localization',
    'author': 'Prointec S.A.',
    'depends': [
        'crm', 
    ],
    'version': '1.0',
    'description': """
CRM Modifications to adapt VIVICON needs
    """,

    'auto_install': False,
    'demo': [
    ],
    'data':[
         'security/ir.model.access.csv',
         'data/crm_vivicon_data.xml',
         'crm_vivicon.xml',
    ],
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
