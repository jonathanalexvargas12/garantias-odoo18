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
        #'views/service_estimate_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}