{
    'name': 'Whatsapp For Lead Generation',
    'version': '14.0.0.1',
    'author': 'Pragmatic TechSoft Pvt Ltd.',
    'website': 'http://pragtech.co.in',
    'category': 'CRM',
    'summary': 'whatsapp connector whatsapp integration odoo Whatsapp crm Whatsapp lead Whatsapp task Whatsapp sale order Whatsapp purchase order Whatsapp invoice Whatsapp payment reminder Whatsapp pos Whatsapp so Whatsapp point of sale whats app communication',
    'description': """
Whatsapp Odoo All In One Integration
====================================
Whatsapp is an immensely popular chatting app used by 1.5 Billion people worldwide.
It has an easy interface and can be used powerfully with Odoo.
Pragmatic has developed an Odoo app which allows users to use the Whatsapp Application to send messages via Odoo.
We can send messages from Contacts, Sales, Accounts invoice, Accounts Payments, Credit Notes, Delivery orders, 
Point of sale, Purchase orders, Project Task, CRM Lead, Payment Reminder, User signup page via the same application. 
Let us have a look at how this works inside Odoo.    
    """,
    'depends': ['crm'],
    'data': [
        'security/ir.model.access.csv',
        'data/utm_data.xml',
        'wizard/send_wp_msg_views.xml',
        'wizard/whatsapp_msg_marketing.xml',
        'views/res_config_settings_view.xml',
        'views/crm_lead_views.xml',
    ],
    'images': ['static/description/whatsapp-for-lead-generation.gif'],
    'live_test_url': 'https://www.pragtech.co.in/company/proposal-form.html?id=103&name=whatsapp-lead-source',
    'price': 49,
    'currency': 'USD',
    'license': 'OPL-1',
    'application': False,
    'auto_install': False,
    'installable': True,
}
