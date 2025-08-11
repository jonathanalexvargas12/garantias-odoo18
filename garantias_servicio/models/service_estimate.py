from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEstimate(models.Model):
    _name = 'service.estimate'
    _description = 'Presupuesto de Servicio Técnico'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Referencia',
        required=True,
        readonly=True,
        default=lambda self: _('New'),
        copy=False
    )
    equipment_id = fields.Many2one(
        'technical.service.equipment',
        string='Equipo',
        required=True,
        ondelete='cascade'
    )
    customer_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=True
    )
    date = fields.Date(
        string='Fecha',
        default=fields.Date.context_today
    )
    estimate_line_ids = fields.One2many(
        'service.estimate.line',
        'estimate_id',
        string='Líneas de Presupuesto'
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Borrador'),
            ('confirmed', 'Confirmado'),
            ('done', 'Realizado'),
            ('canceled', 'Cancelado'),
        ],
        string='Estado',
        default='draft',
        tracking=True
    )
    total_amount = fields.Float(
        string='Total',
        compute='_compute_total_amount',
        store=True
    )

    @api.depends('estimate_line_ids.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.subtotal for line in record.estimate_line_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('service.estimate') or _('New')
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'canceled'})

    def action_draft(self):
        self.write({'state': 'draft'})

class ServiceEstimateLine(models.Model):
    _name = 'service.estimate.line'
    _description = 'Línea de Presupuesto de Servicio Técnico'

    estimate_id = fields.Many2one(
        'service.estimate',
        string='Presupuesto',
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Producto/Servicio',
        required=True
    )
    description = fields.Text(string='Descripción')
    quantity = fields.Float(
        string='Cantidad',
        default=1.0
    )
    unit_price = fields.Float(
        string='Precio Unitario',
        related='product_id.list_price'
    )
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True
    )

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name