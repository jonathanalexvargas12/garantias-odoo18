from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import random

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
        default=lambda self: _('Se creará automáticamente'),
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
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Presupuesto Vinculado',
        readonly=True
    )
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index')
    
    # Nuevo campo para el contador de presupuestos
    sale_order_count = fields.Integer(
        string='Número de Presupuestos',
        compute='_compute_sale_order_count',
        store=False
    )

    @api.depends('entry_date', 'delivery_date')
    def _compute_under_warranty(self):
        for record in self:
            if record.delivery_date and record.entry_date:
                delta = record.delivery_date - record.entry_date
                record.under_warranty = delta.days <= self.WARRANTY_DAYS
            else:
                record.under_warranty = False

    def _compute_sale_order_count(self):
        for record in self:
            # Contar todos los presupuestos relacionados con este equipo
            record.sale_order_count = self.env['sale.order'].search_count([
                ('origin', '=', record.name)
            ])

    @api.constrains('entry_date', 'delivery_date')
    def _check_dates(self):
        for record in self:
            if record.delivery_date and record.entry_date > record.delivery_date:
                raise ValidationError(_('La fecha de ingreso no puede ser posterior a la fecha de entrega.'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                # Generar número aleatorio de 8 dígitos para la referencia
                random_number = str(random.randint(10000000, 99999999))
                vals['name'] = f"REF{random_number}"
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

    def action_view_sale_order(self):
        self.ensure_one()
        # Buscar todos los presupuestos relacionados con este equipo
        sale_orders = self.env['sale.order'].search([('origin', '=', self.name)])
        
        if len(sale_orders) == 1:
            # Si solo hay un presupuesto, abrirlo directamente
            return {
                'type': 'ir.actions.act_window',
                'name': 'Presupuesto',
                'res_model': 'sale.order',
                'res_id': sale_orders.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            # Si hay múltiples presupuestos, mostrar la lista
            return {
                'type': 'ir.actions.act_window',
                'name': 'Presupuestos',
                'res_model': 'sale.order',
                'view_mode': 'tree,form',
                'domain': [('id', 'in', sale_orders.ids)],
                'target': 'current',
            }

    def action_create_estimate(self):
        self.ensure_one()
        
        # Buscar si ya existe un presupuesto con la misma referencia
        existing_order = self.env['sale.order'].search([
            ('origin', '=', self.name),
            ('state', 'in', ['draft', 'sent'])
        ], limit=1)
        
        if existing_order:
            # Si existe un presupuesto en borrador o enviado, redirigir a él
            return {
                'type': 'ir.actions.act_window',
                'name': 'Presupuesto Existente',
                'res_model': 'sale.order',
                'res_id': existing_order.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            # Crear nuevo presupuesto
            sale_order = self.env['sale.order'].create({
                'partner_id': self.customer_id.id,
                'partner_invoice_id': self.customer_id.id,
                'partner_shipping_id': self.customer_id.id,
                'origin': self.name,
                'order_line': [(0, 0, {
                    'product_id': self.product_id.id,
                    'product_uom_qty': 1,
                    'name': f"Reparación de {self.product_id.name}",
                    'price_unit': self.product_id.list_price,
                })]
            })
            
            # Vincular la cotización creada con el equipo
            self.write({'sale_order_id': sale_order.id})
            
            # Actualizar el contador
            self._compute_sale_order_count()
            
            # Abrir la cotización recién creada
            return {
                'type': 'ir.actions.act_window',
                'name': 'Presupuesto de Venta',
                'res_model': 'sale.order',
                'res_id': sale_order.id,
                'view_mode': 'form',
                'target': 'current',
            }