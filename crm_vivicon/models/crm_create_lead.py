#!/usr/bin/python

import sys, getopt
import odoorpc
import json


def get_params(argv):
    server = database = user = password = json_lead = False
    try:
        opts, args = getopt.getopt(argv,"hs:d:u:p:j:",["json_lead="])
    except getopt.GetoptError:
        print( 'crm_create_lead.py -s serverName -d databaseName -u userName -p password -j json_lead_structure')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print( 'crm_create_lead.py -s serverName -d databaseName -u userName -p password -j json_lead_structure')
            sys.exit()
        elif opt in ("-s"):
            server = arg
        elif opt in ("-d"):
            database = arg
        elif opt in ("-u"):
            user = arg
        elif opt in ("-p"):
            password = arg
        elif opt in ("-j"):
            json_lead = (arg)
    print 'Server is "', server
    print 'Database is "', database
    print 'User is "', user
    print 'JSON is "', json_lead
    if not (server and database and user and password and json_lead):
            print( 'crm_create_lead.py -s serverName -d databaseName -u userName -p password -j json_lead_structure')
            sys.exit(2)

    return (server, database, user, password, json_lead)


# -s localhost -d v14_test -u support@cysfuturo.com -p asdfG.9811 -j '{"tipoLead": "contacto", "nombre": "Mario2", "apellido1": "Arias2", "apellido2": "Badilla2", "email": "correo@micorreo.com", "telefono1": "2222-4444", "telefono2": "4444-5555", "proyectoInteres": "Avenir Esmeralda", "observaciones": "este cliente molesta mucho, hay que cobrarle un regargo 10%"}'
# -s localhost -d v14_test -u support@cysfuturo.com -p asdfG.9811 -j '{"tipoLead": "proyecto", "nombreCompleto": "Arturo Lopez Lopez", "email": "correo@micorreo.com", "telefono1": "2222-4444", "relacionPropiedad": "dueño del terreno", "interesPrincipal": "Avenir Esmeralda", "planoCatastro": "100-1341-1029130",  "ubicacion": "Alajuela centro","mensaje": "este cliente molesta mucho, hay que cobrarle un regargo 10%"}'
def main(argv):
    (server, database, user, password, json_lead) = get_params(argv)
    odoo = odoorpc.ODOO(server, port=8069)
    odoo.login(database, user, password)
    crm_lead_obj = odoo.env['crm.lead']
    mail_message_obj = odoo.env['mail.message']
    original_json = json.loads(json_lead)
    tipoLead = original_json["tipoLead"]

    # external_id de el medium y source asiciado a Website
    source_id = odoo.env.ref('utm.utm_source_newsletter')
    medium_id = odoo.env.ref('utm.utm_medium_website')

    if tipoLead == 'contacto':
        final_json = {
            "name": " ".join([original_json["nombre"], original_json["apellido1"], original_json["apellido2"]]),
            "email_from": original_json["email"],
            "phone": original_json["telefono1"],
            "mobile": original_json["telefono2"],
            #"metodo_contacto":"telefono"
            "medium_id": medium_id.id,
            "source_id": source_id.id,
        }
        lead_id = crm_lead_obj.create(final_json)
        mail_message_obj.create({
            'model': 'crm.lead',
            'res_id': lead_id,
            'subject': 'Observaciones',
            'body': observaciones,
        })
        observaciones = '\n'.join([
            u"C O N T A C T O",
            u"Proyecto de interes:" + original_json["proyectoInteres"],
            u"Observaciones:" + original_json["observaciones"],
        ])
        mail_message_obj.create({
            'model': 'crm.lead',
            'res_id': lead_id,
            'subject': 'C O N T A C T O',
            'body': observaciones,
        })
    else:
        final_json = {
            "name": original_json["nombreCompleto"],
            "email_from": original_json["email"],
            "phone": original_json["telefono1"],
            "medium_id": medium_id.id,
            "source_id": source_id.id,
        }
        lead_id = crm_lead_obj.create(final_json)

        observaciones = '\n'.join([
            u"P R O Y E C T O",
            u"Relacion Propiedad:" + original_json["relacionPropiedad"],
            u"Interes Principal:" + original_json["interesPrincipal"],
            u"Plano Catastro:" + original_json["planoCatastro"],
            u"Ubicación:" + original_json["ubicacion"],
            u"Mensaje:" + original_json["mensaje"],
        ])

        mail_message_obj.create({
            'model': 'crm.lead',
            'res_id': lead_id,
            'subject': 'P R O Y E C T O',
            'body': observaciones,
        })

if __name__ == "__main__":
   main(sys.argv[1:])
