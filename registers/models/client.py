"""This are the client template and it's associated functions"""
from odoo import models, fields

class Client(models.Model):
    """Fields and functions for the client object"""
    _name = "client"
    _description = "Registro de Clientes."

    name = fields.Char(string='Nome', required=True)
    age = fields.Integer(string='Idade', required=True)
    obs = fields.Text(string='Obs', required=False)

    def create_client(self):
        """This is the custom function for saving an 'client' object"""
        vals = {
            'name': self.name,
            'age': self.age,
            'email': self.obs,
        }

        self.env['client'].write(vals)
