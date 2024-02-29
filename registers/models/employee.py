"""This is the employee template and it's associated functions"""
import re
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class Employee(models.Model):
    """Fields and functions for the employee object"""
    _name = "employee"
    _description = "Registro de funcionários."

    # code = fields.Integer(string='Codigo', required=True)
    name = fields.Char(string='Nome', required=True)
    email = fields.Char(string='Email', required=False)
    tel = fields.Char(string='Telefone', required=False)
    cpf = fields.Char(string='CPF', required=True)
    # id = fields.Integer(string='ID', required=True)
    address = fields.Char(string='Endereço', required=True)
    cep = fields.Char(string='CEP', required=True)
    # company = fields.Char(string='Empresa', required=True)
    status = fields.Selection([('ativo', 'Ativo'), ('desligado', 'Desligado')])

    def create_employee(self):
        self.status = "ativo"

    @api.constrains('cpf')
    def _check_cpf_size(self):
        """Checks size of the CPF variable to limit different lengths"""
        for rec in self:
            if len(rec.cpf) != 17:
                raise ValidationError(_("O campo CPF está errado. Precisa de 11 dígitos"))
