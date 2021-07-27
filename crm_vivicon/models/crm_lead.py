# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import timedelta

class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _getCategId(self):
        return [('categ_id', '=', self.env.ref('crm_vivicon.product_category_proyectos_crm').id)]

    modelo_interes = fields.Many2many(
        'product.product', 'crm_modelo_interes_rel', 'lead_id', 'tag_id',
        string='Modelos de interés',
        domain=_getCategId, required=True,
        help="Modelos que le interesan al cliente")
    fecha_posible = fields.Date(string='Posible formalización', )
    fecha_reserva = fields.Date(string='Fecha reserva', )
    metodo_pago = fields.Many2one('crm.metodos.pago', string='Método de pago', )
    moneda = fields.Many2one("res.currency", string='Moneda Leads', default=lambda self: self.env.ref('base.USD'))
    monto_pago = fields.Monetary(string='Monto', currency_field='moneda', required=False, readonly=False)  ## required
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
    calificacion = fields.Float(string='Calificacion', digits='Product Price')
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

    @api.onchange('negociacion_solicitada')
    def notificar_negociacion(self):
        if self.negociacion_solicitada:
            email_template = self.env.ref('crm_vivicon.email_template_solicitud_aprobacion', False)
            email_template.with_context(type='binary',
                                        default_type='binary').send_mail(
                                                                self._origin.id,
                                                                raise_exception=False,
                                                                force_send=True)  # default_type='binary'

    @api.onchange('negociacion_aprobada')
    def notificar_negociacion_aprobada(self):
        if self.negociacion_aprobada:
            email_template = self.env.ref('crm_vivicon.email_template_correo_aprobacion', False)
            email_template.with_context(type='binary',
                                        default_type='binary').send_mail(
                                                                self._origin.id,
                                                                raise_exception=False,
                                                                force_send=True)  # default_type='binary'

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

    @api.onchange('user_id')
    def on_change_asesor(self):
        if self.stage_id.sequence < 2:
            self.stage_id = self.env['crm.stage'].search([('name', '=', 'Prospecto')], limit=1)

    @api.onchange('fecha_reserva', 'metodo_pago', 'numero_comprobante', 'monto_pago')
    def opor_reserva(self):
        if self.stage_id.sequence < 3 and self.fecha_reserva and self.metodo_pago and self.numero_comprobante and self.monto_pago:
            self.stage_id = self.env['crm.stage'].search([('name', '=', 'Oport.Reserva')], limit=1)
            if self._origin:
                email_template = self.env.ref('crm_vivicon.email_template_correo_reserva', False)
                email_template.with_context(type='binary',
                                            default_type='binary').send_mail(
                                                                    self._origin.id,
                                                                    raise_exception=False,
                                                                    force_send=True)  # default_type='binary'
            else:
                raise UserError("Debe guardar el registro y volver a editar antes de proceder con la reserva.")

    @api.onchange('req_conozca_cliente', 'req_hoja_datos_propiedad', 'req_copia_cedula')
    def on_change_documentos(self):
        if self.req_conozca_cliente and self.req_hoja_datos_propiedad and self.req_copia_cedula:
            if self.stage_id.sequence < 4:
                self.stage_id = self.env['crm.stage'].search([('name', '=', 'Oport.Documentos')], limit=1)
                email_template = self.env.ref('crm_vivicon.email_template_documentos_cargados', False)
                email_template.with_context(type='binary',
                                            default_type='binary').send_mail(
                                                                    self._origin.id,
                                                                    raise_exception=False,
                                                                    force_send=True)  # default_type='binary'

    @api.onchange('req_cumple_firma_contrato')
    def on_change_cumple_firma(self):
        if self.req_cumple_firma_contrato:
            if self.stage_id.sequence < 5:
                self.stage_id = self.env['crm.stage'].search([('name', '=', 'Reserva Completa')], limit=1)

    @api.onchange('req_fecha_formalizacion')
    def on_change_formalizado(self):
        if self.req_fecha_formalizacion:
            if self.stage_id.sequence < 6:
                self.stage_id = self.env['crm.stage'].search([('name', '=', 'Formalización')], limit=1)

    @api.model
    def _seguimiento_prospectos(self):  # cron
        leads = self.env['crm.lead'].search(
            [('stage_id.sequence', '=', 2),
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
                    email_template.with_context(type='binary',
                                                default_type='binary').send_mail(
                                                                        lead.id,
                                                                        raise_exception=False,
                                                                        force_send=True)  # default_type='binary'
            elif not ultimo_seguimiento or ultimo_seguimiento < today:  # ya hay que programar un nuevo seguimiento
                if not ultimo_seguimiento:
                    ultimo_seguimiento = today

                if lead.nivel_seguimiento < 3:
                    proximo_seguimiento = ultimo_seguimiento + timedelta(days=3)
                elif lead.frecuencia_seguimiento == 'semanal':
                    proximo_seguimiento = ultimo_seguimiento + timedelta(days=7)
                elif lead.frecuencia_seguimiento == 'semanal':
                    proximo_seguimiento = ultimo_seguimiento + timedelta(days=14)
                else:
                    proximo_seguimiento = ultimo_seguimiento + timedelta(days=30)

                lead.nivel_seguimiento += 1
                lead.fecha_ultimo_seguimiento = proximo_seguimiento
                values = {
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'note': 'Solicitud de aprobación de negociación. ',
                    'res_id': lead.id,
                    'res_model_id': leads_model_id,
                    'user_id': lead.user_id.id,
                    'date_deadline': proximo_seguimiento,
                    'automated': True,
                }
                activity = self.env['mail.activity'].sudo().create(values)
                activity._onchange_activity_type_id()
