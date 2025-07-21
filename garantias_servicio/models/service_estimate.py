from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ServiceEstimate(models.Model):
    # Al cambiar el equipo, se asigna automáticamente el cliente relacionado
    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id:
            self.customer_id = self.equipment_id.customer_id
    _name = 'service.estimate'
    _description = 'Presupuesto de Servicio Técnico'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Cédula del propietario, solo admite números
    name = fields.Char(
        string='Cédula del Propietario',
        required=True,
        readonly=False,
        default=lambda self: _('Cedula No Ingresada'),
        copy=False
    )
    # Validación: la cédula solo puede contener números

    @api.constrains('name')
    def _check_cedula_numeric(self):
        for record in self:
            if record.name and not record.name.isdigit():
                raise ValidationError(_('La cédula del propietario solo puede contener números.'))
    # Relación con el equipo técnico
    equipment_id = fields.Many2one(
        'technical.service.equipment',
        string='Equipo',
        required=True,
        ondelete='cascade'
    )
    # Cliente asociado, solo lectura y se asigna automáticamente
    customer_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        required=False,
        readonly=True
    )
    # Fecha del presupuesto
    date = fields.Date(
        string='Fecha',
        default=fields.Date.context_today
    )
    # Líneas de presupuesto asociadas
    estimate_line_ids = fields.One2many(
        'service.estimate.line',
        'estimate_id',
        string='Líneas de Presupuesto'
    )
    # Estado del presupuesto
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
    # Total calculado automáticamente
    total_amount = fields.Float(
        string='Total',
        compute='_compute_total_amount',
        store=True
    )

    # Calcula el total sumando los subtotales de las líneas
    @api.depends('estimate_line_ids.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.subtotal for line in record.estimate_line_ids)

    # Al crear el registro, asigna la cédula si es nueva y el cliente si hay equipo
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('service.estimate') or _('New')
            # Asignar cliente automáticamente si hay equipo seleccionado
            if vals.get('equipment_id') and not vals.get('customer_id'):
                equipo = self.env['technical.service.equipment'].browse(vals['equipment_id'])
                if equipo and equipo.customer_id:
                    vals['customer_id'] = equipo.customer_id.id
        return super().create(vals_list)

    # Acciones para cambiar el estado del presupuesto
    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'canceled'})

    def action_draft(self):
        self.write({'state': 'draft'})

class ServiceEstimateLine(models.Model):
    # Modelo para las líneas de presupuesto
    _name = 'service.estimate.line'
    _description = 'Línea de Presupuesto de Servicio Técnico'

    # Relación con el presupuesto principal
    estimate_id = fields.Many2one(
        'service.estimate',
        string='Presupuesto',
        ondelete='cascade'
    )
    # Producto o servicio asociado
    product_id = fields.Many2one(
        'product.product',
        string='Producto/Servicio',
        required=True
    )
    # Descripción del producto o servicio
    description = fields.Text(string='Descripción')
    # Cantidad solicitada
    quantity = fields.Float(
        string='Cantidad',
        default=1.0
    )
    # Precio unitario, relacionado con el producto
    unit_price = fields.Float(
        string='Precio Unitario',
        related='product_id.list_price'
    )
    # Subtotal calculado automáticamente
    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True
    )

    # Calcula el subtotal de la línea
    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.quantity * line.unit_price

    # Al cambiar el producto, actualiza la descripción automáticamente
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.description = self.product_id.name