# ------------------------------------------------------------------------------
# Archivo: __manifest__.py
# Descripción: Manifest del módulo 'Gestión de Servicio Técnico' para Odoo 18
# Este archivo define la metadata, dependencias, vistas, seguridad y configuración
# general del módulo. Es fundamental para la instalación y funcionamiento correcto
# del módulo dentro de Odoo.
# ------------------------------------------------------------------------------
#
# Campos principales:
# - name: Nombre del módulo que aparecerá en Odoo.
# - version: Versión actual del módulo.
# - summary: Resumen breve del propósito del módulo.
# - description: Descripción detallada de las funcionalidades y alcance.
# - author/website: Información del desarrollador responsable.
# - category: Categoría en la que se clasifica el módulo.
# - depends: Lista de módulos de los que depende para funcionar correctamente.
# - data: Archivos XML y CSV que definen vistas, seguridad y otros recursos.
# - demo: Archivos de datos de demostración (si existen).
# - installable: Indica si el módulo puede instalarse.
# - application: Si el módulo es una aplicación principal.
# - license: Tipo de licencia bajo la que se distribuye el módulo.
# ------------------------------------------------------------------------------
{
    'name': 'Gestión de Servicio Técnico',
    'version': '1.0.1',
    'summary': 'Módulo para la gestión integral de servicio técnico con administración de garantías',
    'description': """
        Módulo para la gestión de equipos en servicio técnico, con control de garantías,
        estados de reparación y generación de presupuestos.
    """,
    'author': 'Jonathan Alexander Vargas',
    'website': 'jonathanvargas@gmail.com',
    'category': 'Services',
    'depends': ['base', 'product', 'sale'],
    'data': [
        'views/technical_service_views.xml',
        'views/service_estimate_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}