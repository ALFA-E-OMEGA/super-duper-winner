from odoo import models, fields

class Client(models.Model):
    _name = "client"
    _description = "Registro de Clientes."

    name = fields.Char(string='Nome', required=True)
    age = fields.Integer(string='Idade', required=True)
    obs = fields.Text(string='Obs', required=False)