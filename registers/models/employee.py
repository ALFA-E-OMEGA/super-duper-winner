"""This are the employee template and it's associated functions"""
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
    status = fields.Selection([('ativo', 'Ativo'), ('desligado', 'Desligado')], required=True)

    def create_employee(self):
        """This is the custom function for saving an 'employee' object"""
        vals = {
            'name': self.name,
            'email': self.email,
            'tel': self.tel,
            'cpf': self.cpf,
            'address': self.address,
            'cep': self.cep,
            'status': self.status,
        }

        self.env['employee'].write(vals)

    @api.constrains('cpf')
    def _validate_cpf(self):
        """Checks size of the CPF variable to limit different lengths"""
        for rec in self:
            if len(rec.cpf) != 11:
                raise ValidationError(_("O campo 'CPF' está com o tamanho incorreto. Precisa de 11 dígitos"))
            if (rec.cpf).isnumeric() != True:
                raise ValidationError(_("O campo 'CPF' contém carácteres inválidos. O campo deve conter apenas números"))

    @api.constrains('cep')
    def _validate_cep(self):
        """Checks size of the CEP variable to limit different lengths"""
        for rec in self:
            if len(rec.cep) != 8:
                raise ValidationError(_("O campo 'CEP' está está com o tamanho incorreto. Precisa de 8 dígitos"))
            if (rec.cep).isnumeric() != True:
                raise ValidationError(_("O campo 'CEP' contém carácteres inválidos. O campo deve conter apenas números"))
