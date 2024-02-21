# -*- coding: utf-8 -*-
{
    'name' : 'Cadastro',
    'author': 'Alfa e Omega',
    'version' : '1.0',
    'summary': 'Módulo de Cadastro',
    'sequence': -1,
    'description': """Este é o módulo que lida com os cadastros.""",
    'category': 'JP',
    'depends' : ['base', 'web', 'sale', 'board'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/employee.xml',
        'views/client.xml',
        'views/patrimony.xml',

    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {
         'web.assets_backend':[
             'registers/static/src/css/createEmployeeStyle.css',
             'registers/static/src/js/createEmployee.js',
         ]
    },
}
