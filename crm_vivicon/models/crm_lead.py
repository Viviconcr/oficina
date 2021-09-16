# -*- coding: utf-8 -*-
from __future__ import print_function
import functools
import traceback
import sys

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

from datetime import timedelta, datetime
import logging
_logger = logging.getLogger(__name__)

"""
INDENT = 4*' '

def stacktrace(func):
    @functools.wraps(func)
    def wrapped(*args, **kwds):
        # Get all but last line returned by traceback.format_stack()
        # which is the line below.
        callstack = '\n'.join([INDENT+line.strip() for line in traceback.format_stack()][:-1])
        _logger.error('PROINTEC - {}() called:'.format(func.__name__))
        _logger.error(callstack)
        return func(*args, **kwds)

    return wrapped
"""

class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _getCategId(self):
        return [('categ_id', '=', self.env.ref('crm_vivicon.product_category_proyectos_crm').id)]

    def _inverseStage(self):
        if self.stage_id.name == 'Oport.Reserva':
            email_template = self.env.ref('crm_vivicon.email_template_correo_reserva', False)
            email_template.with_context(type='binary',
                                        default_type='binary').send_mail(
                                                                self.id,
                                                                raise_exception=False,
                                                                force_send=True)  # default_type='binary'
        elif self.stage_id.name == 'Oport.Documentos':
            email_template = self.env.ref('crm_vivicon.email_template_documentos_cargados', False)
            email_template.with_context(type='binary',
                                        default_type='binary').send_mail(
                                                                self.id,
                                                                raise_exception=False,
                                                                force_send=True)  # default_type='binary'

    modelo_interes = fields.Many2many(
        'product.product', 'crm_modelo_interes_rel', 'lead_id', 'tag_id',
        string='Modelos de interés',
        domain=_getCategId, required=False,
        help="Modelos que le interesan al cliente")
    modelo_seleccionado_id = fields.Many2one(
        'product.product', 
        string='Modelo seleccionado',
        domain=_getCategId, 
        help="Modelo seleccionado por el cliente") 

    casa_seleccionada_id = fields.Many2one('stock.production.lot', string='Casa seleccionada',
        help="Casa seleccionada por el cliente")       
    fecha_posible = fields.Date(string='Posible formalización', )
    fecha_reserva = fields.Date(string='Fecha reserva', )
    metodo_pago = fields.Many2one('crm.metodos.pago', string='Método de pago', )
    moneda = fields.Many2one("res.currency", string='Moneda Leads', default=lambda self: self.env.ref('base.USD'))
    monto_pago = fields.Monetary(string='Monto de reserva', currency_field='moneda', required=False, readonly=False)  ## required
    numero_comprobante = fields.Char('# Comprobante')
    copia_comprobante = fields.Binary( string="Copia de comprobante", required=False, copy=False, attachment=True)


    # convertir a adjunto estos campos:
    req_conozca_cliente = fields.Binary( string="Formulario Conozca su cliente", required=False, copy=False, attachment=True)
    req_hoja_datos_propiedad = fields.Binary( string="Hoja de datos de Propiedad", required=False, copy=False, attachment=True)
    req_copia_cedula = fields.Binary( string="Copia de cédula", required=False, copy=False, attachment=True)

    req_cumple_firma_contrato = fields.Boolean(string='Cumple con la firma del contrato', )
    #req_contrato_listo = fields.Boolean(string='Contrato listo', )
    #req_fecha_contrato_listo = fields.Date(string='Contrato listo', )

    req_fecha_formalizacion = fields.Date(string='Fecha de formalización', )
    entidad_bancaria = fields.Char('Entidad bancaria')

    porcentaje_plazo = fields.Float(string='Porcentaje de Plazo (%)', digits='Product Price')
    porcentaje_interes = fields.Float(string='Porcentaje de Interés (%)', digits='Product Price')
    porcentaje_capacidad_economica = fields.Float(string='Porcentaje de Capacidad económica (%)', digits='Product Price')
    calificacion = fields.Float(string='Calificación', digits='Product Price')
    plazo_decidir = fields.Selection([
        ('100', 'Inmediata'),
        ('80', 'Menos de 3 meses'),
        ('60', 'Entre 3 y 6 meses'),
        ('40', 'Más de 6 meses'),
        ('20', 'Más de 1 año'),
        ('0', 'No parece que vaya a tomar una decisión'),
    ], string='Plazo para decidir', default=False, )
    interes_disposicion = fields.Selection([
        ('100', 'Excelente interés'),
        ('80', 'Muy buen interés'),
        ('60', 'Buen interés'),
        ('40', 'Algún interés'),
        ('20', 'Poco interés'),
        ('0', 'No tiene ningún interés en el proyecto'),
    ], string='Interés / Disposición', default=False, )
    capacidad_economica = fields.Selection([
        ('100', 'Cuenta con recursos propios/prima y precalificación bancaria'),
        ('80', 'Tiene mayoría de la prima y está precalificado'),
        ('60', 'Tiene posibilidades de completar la prima y cumple ingreso requerido'),
        ('40', 'Ingresos insuficientes o no demostrables o requiere codeudor'),
        ('20', 'Poca capacidad económica'),
        ('0', 'No tiene capacidad económica'),
    ], string='Capacidad Económica', default=False, )
    metodo_contacto = fields.Selection([
        ('telefono', 'Llamada telefónica'),
        ('mensaje', 'Mensaje texto/Whatsapp'),
        ('correo', 'Correo electrónico'),
    ], string='Medio preferido de Contacto', default=False, required=False )  ## required
    frecuencia_seguimiento = fields.Selection([
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
    ], string='Frecuencia de seguimiento', readonly=False, )
    nivel_seguimiento = fields.Integer('Nivel de seguimiento', default=0)
    fecha_ultimo_seguimiento = fields.Date(string='Último seguimiento programado', )

    negociacion_solicitada = fields.Boolean(string='Solicitar aprobación', help="Bloquear la negociación y solicitar aprobación" )
    negociacion_aprobada = fields.Boolean(string='Negociación aprobada', )
    negociacion_ids = fields.One2many('negociacion.crm', 'lead_id', 'Negociaciones')

    banco = fields.Char(string = 'Banco')
    observaciones = fields.Text(string='Observaciones')

    seguimiento_ids = fields.One2many('seguimiento.crm', 'lead_id', 'Detalle')
        
    # duplicados
    cantidad_similares = fields.Integer(string='Cantidad similares', copy=False, store=True)
    es_similar_a_otro = fields.Boolean(string='Posible Duplicación', copy=False, default=False,
                                        help='La oportunidad tiene algunos datos que son similares a otras existentes', )
    similar_autorizado_por = fields.Many2one('res.users', string='Liberado por', copy=False, )

    lead_similares_ids = fields.One2many(comodel_name='xcrm.lead.similares', 
                                        inverse_name='lead_id', 
                                        string='Lead Similares',
                                        copy=False)
    stage_id = fields.Many2one(inverse=_inverseStage)
    stage_sequence = fields.Integer(string='Stage Sequence', related='stage_id.sequence', store=True, index=True, readonly=True)

    crm_project_id = fields.Many2one('xcrm.projects', string='Proyecto')
    other_phone = fields.Char(string='Otros Teléfonos', copy=False)
    es_contacto = fields.Boolean(string='Es contacto', default=True)
    x_estado_mensaje = fields.Selection([
        ('normal', 'Leído'),
        ('done', 'Sin Leer')], string='Estado Mensajes',
        copy=False, default='normal', required=True)

    @api.model
    def create(self, vals_list):
        res = super(Lead, self).create(vals_list)
        if len(res) == 1:
            similares = res.calcula_similares()
            if similares and similares.get('cantidad_similares') > 0:
                for vid in similares.get('leads_similares'):
                    res.env['xcrm.lead.similares'].sudo().create({'lead_id': res.id, 'lead_similar_id': vid})
                res.cantidad_similares = similares.get('cantidad_similares')
                res.es_similar_a_otro = True
        return res

    #@stacktrace
    def write(self, vals):
        # if len(self) == 1 and self.active and not self.stage_id.is_won:
        
        # similares
        similares = None
        if len(self) == 1 and self.active: 
            new_es_similar_a_otro = vals.get('es_similar_a_otro')            
            if self.es_similar_a_otro and new_es_similar_a_otro != None and not new_es_similar_a_otro:
                vals.update({'similar_autorizado_por': self.env.uid })
            elif (self.stage_id.sequence <= 2 
                    and (not self.cantidad_similares or self.cantidad_similares == 0 or (self.cantidad_similares > 0 and not self.similar_autorizado_por)) ):
                similares = self.calcula_similares()
                if similares and similares.get('cantidad_similares') > 0:
                    vals['cantidad_similares'] = similares.get('cantidad_similares')
                    vals['es_similar_a_otro'] = True
                elif self.cantidad_similares > 0:
                    # No devolvió similares, entonces limpia lo que tenía antes
                    vals['cantidad_similares'] = 0
                    vals['es_similar_a_otro'] = False

        # graba los datos del Lead 
        res = super(Lead, self).write(vals)

        # similares
        if len(self) == 1:
            if self.cantidad_similares > 0:
                self.lead_similares_ids.unlink()        
            if similares and similares.get('cantidad_similares') > 0:
                for vid in similares.get('leads_similares'):
                    self.env['xcrm.lead.similares'].sudo().create({'lead_id': self.id, 'lead_similar_id': vid})
       
            if 'user_id' in vals or self.es_contacto == False:
                if self.stage_id == self.env['crm.stage'].search([('name', '=', 'Contacto')], limit=1):
                    vals['stage_id']  = self.env['crm.stage'].search([('name', '=', 'Prospecto')], limit=1)
                    self.stage_id = self.env['crm.stage'].search([('name', '=', 'Prospecto')], limit=1)

        return res

    #@stacktrace
    def calcula_similares(self):        
        vals = {}
        fref = datetime.today() - timedelta(days=365)   # 1 año hacia atras
        fdesde_str = fref.strftime('%Y-%m-%d')
        leads_similares = []            
        cantidad = 0
        leads = self.env['crm.lead'].search([('active','=',True), ('create_date','>=',fdesde_str)])
        for r in leads:
            if r.id != self.id:
                vid = None
                email = None if not self.email_from else self.email_from.replace(',',';').replace(' ','').upper().split(';')
                phone = None if not self.phone else self.phone.replace(',',';').replace(' ','').upper().split(';')
                #---- Revisa si existen otros lead con Telefono y correos similares
                name = ' '.join(self.name.split())    # divide el nombre en las partes que tiene y luego las uno con solo un espacio
                dat = ' '.join(r.name.split())
                if name == dat:
                    vid = r.id
                # verifica si tienen correos en comun
                if not vid and self.email_from and r.email_from:
                    dat = r.email_from.replace(',',';').replace(' ','').upper().split(';')
                    if (set(email) & set(dat)):
                        vid = r.id
                # verifica si tienen teléfonos en comun
                if not vid and self.phone and r.phone:
                    dat = r.phone.replace(',',';').replace(' ','').upper().split(';')
                    if (set(phone) & set(dat)):
                        vid = r.id

                #---- Revisa si existen otros lead donde los datos de contactos sean similares a los de este lead
                if not vid and r.contact_name:
                    dat = ' '.join(r.contact_name.split())
                    if name == dat:
                        vid = r.id
                # verifica si el correo del contacto es identico al de este lead
                if not vid and email and r.function:
                    dat = r.function.replace(',',';').replace(' ','').upper().split(';')
                    if (set(email) & set(dat)):
                        vid = r.id
                # verifica si tienen teléfonos en comun datos de contactos de otros lead
                if not vid and phone and r.mobile:
                    dat = r.mobile.replace(',',';').replace(' ','').upper().split(';')
                    if (set(phone) & set(dat)):
                        vid = r.id
                #
                if vid:
                    leads_similares.append( vid )
                    cantidad += 1
        vals['cantidad_similares'] = cantidad
        vals['es_similar_a_otro'] = True
        vals['leads_similares'] = leads_similares
        return vals


    #@stacktrace
    @api.onchange('negociacion_solicitada')
    def notificar_negociacion(self):
        if self.negociacion_solicitada:
            email_template = self.env.ref('crm_vivicon.email_template_solicitud_aprobacion', False)
            email_template.with_context(type='binary',
                                        default_type='binary').send_mail(
                                                                self._origin.id,
                                                                raise_exception=False,
                                                                force_send=True)  # default_type='binary'

    #@stacktrace
    @api.onchange('negociacion_aprobada')
    def notificar_negociacion_aprobada(self):
        if self.negociacion_aprobada:
            email_template = self.env.ref('crm_vivicon.email_template_correo_aprobacion', False)
            email_template.with_context(type='binary',
                                        default_type='binary').send_mail(
                                                                self._origin.id,
                                                                raise_exception=False,
                                                                force_send=True)  # default_type='binary'

    #@stacktrace
    @api.onchange('plazo_decidir', 'interes_disposicion', 'capacidad_economica')
    def on_change_calificacion(self):
        total = 0
        total = (int(self.plazo_decidir) + int(self.interes_disposicion) + int(self.capacidad_economica)) / 3.0
        self.calificacion = total

        if self.stage_id.name == 'Contacto':
            self.stage_id = self.env['crm.stage'].search([('name', '=', 'Prospecto')], limit=1)

        if total < 50:
            self.frecuencia_seguimiento = 'mensual'
        elif total < 70:
            self.frecuencia_seguimiento = 'quincenal'
        else:
            self.frecuencia_seguimiento = 'semanal'

    #@stacktrace
    @api.onchange('user_id')
    def on_change_asesor(self):
        if self.stage_id.sequence < 2:
            self.es_contacto = False

    #@stacktrace
    @api.onchange('fecha_reserva', 'metodo_pago', 'numero_comprobante', 'monto_pago')
    def opor_reserva(self):
        if self.stage_id.sequence < 3 and self.fecha_reserva and self.metodo_pago and self.numero_comprobante and self.monto_pago:
            self.stage_id = self.env['crm.stage'].search([('name', '=', 'Oport.Reserva')], limit=1)

    #@stacktrace
    @api.onchange('req_conozca_cliente', 'req_hoja_datos_propiedad', 'req_copia_cedula')
    def on_change_documentos(self):
        if self.stage_id.sequence < 4 and self.req_conozca_cliente and self.req_hoja_datos_propiedad and self.req_copia_cedula:
            self.stage_id = self.env['crm.stage'].search([('name', '=', 'Oport.Documentos')], limit=1)

    #@stacktrace
    @api.onchange('req_cumple_firma_contrato')
    def on_change_cumple_firma(self):
        if self.stage_id.sequence < 5 and self.req_cumple_firma_contrato:
            self.stage_id = self.env['crm.stage'].search([('name', '=', 'Reserva Completa')], limit=1)

    #@stacktrace
    @api.onchange('req_fecha_formalizacion')
    def on_change_formalizado(self):
        if self.stage_id.sequence < 6 and self.req_fecha_formalizacion:
            self.stage_id = self.env['crm.stage'].search([('name', '=', 'Formalización')], limit=1)

    #@stacktrace
    @api.model
    def _seguimiento_prospectos(self):  # cron
        leads = self.env['crm.lead'].search(
            [('stage_id.sequence', '=', 2),
             ('user_id', '!=', False),
             #('nivel_seguimiento', '<=', 2)  # we need to confirm if followup is needed for all leads in stage 2
            ],
        )
        leads_model_id = self.env['ir.model']._get('crm.lead').id
        total_leads = len(leads)
        current_lead = 0
        today = fields.Date.context_today(self)

        for lead in leads:
            current_lead += 1

            # mail.activity only holds pending activities.  When done, they are deleted and created as messages in chatter
            overdue_activities = self.env['mail.activity'].search(
                [('res_model_id', '=', leads_model_id),
                 ('automated','=', True),
                 ('res_id', '=', lead.id),
                 ('date_deadline', '<', today)
                ],
            )
            ultimo_seguimiento = lead.fecha_ultimo_seguimiento
            if overdue_activities:
                if ultimo_seguimiento != today:  # caso contrario ya lo movimos y enviamos correo, por eso no se debe volver a enviar
                    lead.fecha_ultimo_seguimiento = today  # mover fecha para que no se genere una nueva si apenas se va a atender la que está pendiente
                    email_template = self.env.ref('crm_vivicon.email_template_actividad_atrasada', False)
                    # email_template.with_context(type='binary',
                    #                             default_type='binary').send_mail(
                    #                                                     lead.id,
                    #                                                     raise_exception=False,
                    #                                                     force_send=True)  # default_type='binary'
            elif not ultimo_seguimiento or ultimo_seguimiento < today:  # ya hay que programar un nuevo seguimiento
                if not ultimo_seguimiento:
                    ultimo_seguimiento = today

                if lead.nivel_seguimiento < 3:
                    proximo_seguimiento = ultimo_seguimiento + timedelta(days=3)
                elif lead.frecuencia_seguimiento == 'semanal':
                    proximo_seguimiento = ultimo_seguimiento + timedelta(days=7)
                elif lead.frecuencia_seguimiento == 'quincenal':
                    proximo_seguimiento = ultimo_seguimiento + timedelta(days=14)
                else:
                    proximo_seguimiento = ultimo_seguimiento + timedelta(days=30)

                lead.nivel_seguimiento += 1
                lead.fecha_ultimo_seguimiento = proximo_seguimiento
                values = {
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'note': 'Por favor dar seguimiento al cliente. ',
                    'res_id': lead.id,
                    'res_model_id': leads_model_id,
                    'user_id': lead.user_id.id,
                    'date_deadline': proximo_seguimiento,
                    'automated': True,
                }
                activity = self.env['mail.activity'].sudo().create(values)
                #activity._onchange_activity_type_id()
