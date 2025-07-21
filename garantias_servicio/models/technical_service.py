from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class TechnicalServiceEquipment(models.Model):
    # Genera una referencia única para el equipo
    def _generate_unique_reference(self):
        import random
        digits = '0123456789'
        for _ in range(100):
            serial = 'REF' + ''.join(random.choices(digits, k=8))
            if not self.env['technical.service.equipment'].search_count([('name', '=', serial)]):
                return serial
        raise ValidationError(_('No se pudo generar una referencia única.'))
    _name = 'technical.service.equipment'
    _description = 'Equipo de Servicio Técnico'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'entry_date desc'

    # Días de garantía para el equipo
    WARRANTY_DAYS = 90

    # Referencia única del equipo, generada automáticamente
    name = fields.Char(
        string='Referencia',
        required=True,
        readonly=True,
        default=lambda self: _('New'),
        copy=False
    )
    # Producto relacionado con el equipo
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        domain=[('type', '=', 'product')]
    )
    # Fecha de ingreso del equipo al servicio técnico
    entry_date = fields.Date(
        string='Fecha de Ingreso',
        required=True,
        default=fields.Date.context_today
    )
    # Fecha de entrega del equipo
    delivery_date = fields.Date(string='Fecha de Entrega')
    # Estado del equipo en el proceso de servicio técnico
    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('repair', 'En Reparación'),
            ('scrapped', 'Dado de Baja'),
            ('delivered', 'Entregado'),
        ],
        string='Estado',
        default='draft',
        tracking=True
    )
    # Indica si el equipo está en garantía
    under_warranty = fields.Boolean(
        string='En Garantía',
        compute='_compute_under_warranty',
        store=True
    )
    # Cliente propietario del equipo
    customer_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True
    )
    # Descripción del problema reportado
    description = fields.Text(string='Descripción del Problema')
    # Presupuestos asociados al equipo
    estimate_ids = fields.One2many(
        'service.estimate',
        'equipment_id',
        string='Presupuestos'
    )
    # Indica si el registro está activo
    active = fields.Boolean(default=True)
    # Índice de color para la vista kanban
    color = fields.Integer(string='Color Index')

    # Calcula si el equipo está en garantía según las fechas
    @api.depends('entry_date', 'delivery_date')
    def _compute_under_warranty(self):
        for record in self:
            if record.delivery_date and record.entry_date:
                delta = record.delivery_date - record.entry_date
                record.under_warranty = delta.days <= self.WARRANTY_DAYS
            else:
                record.under_warranty = False

    # Valida que la fecha de ingreso no sea posterior a la de entrega
    @api.constrains('entry_date', 'delivery_date')
    def _check_dates(self):
        for record in self:
            if record.delivery_date and record.entry_date > record.delivery_date:
                raise ValidationError(_('La fecha de ingreso no puede ser posterior a la fecha de entrega.'))

    # Al crear el registro, genera la referencia única automáticamente
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self._generate_unique_reference()
        return super().create(vals_list)

    # Acciones para cambiar el estado del equipo
    def action_confirm_repair(self):
        self.write({'state': 'repair'})

    def action_scrap(self):
        self.write({'state': 'scrapped'})

    def action_deliver(self):
        self.write({
            'state': 'delivered',
            'delivery_date': fields.Date.context_today(self)
        })

    def action_draft(self):
        self.write({'state': 'draft'})

    # Acción para crear un presupuesto asociado al equipo
    def action_create_estimate(self):
        self.ensure_one()
        estimate = self.env['service.estimate'].create({
            'equipment_id': self.id,
            'customer_id': self.customer_id.id,
        })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Presupuesto',
            'res_model': 'service.estimate',
            'res_id': estimate.id,
            'view_mode': 'form',
            'target': 'current',
        }