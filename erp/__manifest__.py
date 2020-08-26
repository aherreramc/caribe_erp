# -*- coding: utf-8 -*-
{
    'name': "Erp",

    'summary': """Sistema Erp para importadores""",

    'description': """

    """,

    'author': "Alejandro Herrera Martínez",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Aplication',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'sale'],

    'depends': [
        'base',
        'stock',
        'sale'
    ],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # Views

        # Nomencladores
        'views/nomencladores/tipo_de_espiga.xml',
        'views/nomencladores/tipo_de_producto.xml',
        'views/nomencladores/potencia.xml',
        'views/nomencladores/material.xml',
        'views/nomencladores/marca.xml',
        'views/nomencladores/embalaje.xml',
        'views/nomencladores/puerto.xml',
        'views/nomencladores/representante_cliente.xml',
        'views/nomencladores/dias_para_cobros_y_pagos.xml',
        'views/nomencladores/etapa.xml',
        'views/nomencladores/pago_nomenclador.xml',
        'views/nomencladores/garantia.xml',
        'views/nomencladores/firma.xml',
        'views/nomencladores/degradation_type.xml',
        'views/nomencladores/product_template_rondover.xml',

        'views/nomencladores/menus.xml',

        # Reportes
        # 'report/nomencladores/product_label_report.xml',
        'report/operaciones/quotations_report.xml',
        'report/operaciones/quotations_report.xml',

        'report/operaciones/reportes_operaciones_config.xml',
        'report/reportes_config.xml',

        # security
        'security/security.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
