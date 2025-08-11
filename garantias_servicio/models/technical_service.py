from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta

class TechnicalServiceEquipment(models.Model):
    _name = 'technical.service.equipment'
    _description = 'Equipo de Servicio Técnico'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'entry_date desc'

    WARRANTY_DAYS = 90  # Período de garantía en días

    name = fields.Char(
        string='Referencia',
        required=True,
        readonly=True,
        default=lambda self: _('New'),
        copy=False
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        required=True,
        domain="[('categ_id', 'in', [12])]"  
       
    )
    entry_date = fields.Date(
        string='Fecha de Ingreso',
        required=True,
        default=fields.Date.context_today
    )
    delivery_date = fields.Date(string='Fecha de Entrega')
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
    under_warranty = fields.Boolean(
        string='En Garantía',
        compute='_compute_under_warranty',
        store=True
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True
    )
    description = fields.Text(string='Descripción del Problema')
    estimate_ids = fields.One2many(
        'service.estimate',
        'equipment_id',
        string='Presupuestos'
    )
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')

    @api.depends('entry_date', 'delivery_date')
    def _compute_under_warranty(self):
        for record in self:
            if record.delivery_date and record.entry_date:
                delta = record.delivery_date - record.entry_date
                record.under_warranty = delta.days <= self.WARRANTY_DAYS
            else:
                record.under_warranty = False

    @api.constrains('entry_date', 'delivery_date')
    def _check_dates(self):
        for record in self:
            if record.delivery_date and record.entry_date > record.delivery_date:
                raise ValidationError(_('La fecha de ingreso no puede ser posterior a la fecha de entrega.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('technical.service.equipment') or _('New')
        return super().create(vals_list)

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