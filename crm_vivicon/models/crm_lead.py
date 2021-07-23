# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


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
    monto_pago = fields.Monetary(string='Monto', currency_field='company_currency', required=False, readonly=False)  ## required
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


    negociacion_solicitada = fields.Boolean(string='Solicitar aprobación', help="Bloquear la negociación y solicitar aprobación" )
    negociacion_aprobada = fields.Boolean(string='Negociación aprobada', )
    negociacion_ids = fields.One2many('negociacion.crm', 'lead_id', 'Negociaciones')

    @api.onchange('negociacion_solicitada')
    def notificar_negociacion(self):
        if self.negociacion_solicitada:
            values = {
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'note': 'Solicitud de aprobación de negociación. ',
                'res_id': self.ids[0],
                'res_model_id': self.env['ir.model']._get('crm.lead').id,
                'user_id': self.user_id.id,
            }
            activity = self.env['mail.activity'].sudo().create(values)
            activity._onchange_activity_type_id()


    @api.onchange('negociacion_aprobada')
    def notificar_negociacion_aprobada(self):
        if self.negociacion_aprobada:
            values = {
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'note': 'Solicitud de negociación APROBADA. ',
                'res_id': self.ids[0],
                'res_model_id': self.env['ir.model']._get('crm.lead').id,
                'user_id': self.user_id.id,
            }
            activity = self.env['mail.activity'].sudo().create(values)
            activity._onchange_activity_type_id()

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

            values = {
                'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                'note': 'Reserva se completó. ',
                'res_id': self.ids[0],
                'res_model_id': self.env['ir.model']._get('crm.lead').id,
                'user_id': self.user_id.id,
            }
            activity = self.env['mail.activity'].sudo().create(values)
            activity._onchange_activity_type_id()

    @api.onchange('req_conozca_cliente', 'req_hoja_datos_propiedad', 'req_copia_cedula')
    def on_change_documentos(self):
        if req_conozca_cliente and req_hoja_datos_propiedad and req_copia_cedula:
            if self.stage_id.sequence < 5:
                self.stage_id = self.env['crm.stage'].search([('name', '=', 'Reserva Completa')], limit=1)

    @api.onchange('req_cumple_firma_contrato')
    def on_change_cumple_firma(self):
        if req_conozca_cliente and req_hoja_datos_propiedad and req_copia_cedula:
            if self.stage_id.sequence < 6:
                self.stage_id = self.env['crm.stage'].search([('name', '=', 'Formalización')], limit=1)
