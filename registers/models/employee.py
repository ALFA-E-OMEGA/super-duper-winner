"""This are the employee template and it's associated functions"""
# pylint: skip-file
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import re

regex_email = re.compile(r'([A-Za-z0-9]{1,24}+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9]+(\.[A-Z|a-z]{2,12})+')

class Employee(models.Model):
    """Fields and functions for the employee object"""

    def _validate_cpf_digits(self, cpf_string):
        
        numbers = [int(digit) for digit in cpf_string if digit.isdigit()]

        sum_of_products = sum(a*b for a, b in zip(numbers[0:9], range(10, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[9] != expected_digit:
            return False
        
        sum_of_products = sum(a*b for a, b in zip(numbers[0:10], range(11, 1, -1)))
        expected_digit = (sum_of_products * 10 % 11) % 10
        if numbers[10] != expected_digit:
            return False
        
        return True
    
    _name = "employee"
    _description = "Registro de funcionários."

    name = fields.Char(string='Nome', required=True)
    email = fields.Char(string='Email', required=False)
    tel_one = fields.Char(string='Telefone 1', required=True)
    tel_two = fields.Char(string='Telefone 2', required=False)
    cpf = fields.Char(string='CPF', required=True)
    address = fields.Char(string='Endereço', required=False)
    cep = fields.Char(string='CEP', required=False)
    pis_pasep = fields.Char(string='PIS-PASEP', required=False)
    cart_trabalho = fields.Char(string='Carteira de Trabalho', required=False)
    rg = fields.Char(string='RG', required=True)
    status = fields.Selection([('ativo', 'Ativo'), ('desligado', 'Desligado')], required=True)

    def create_employee(self):
        """This is the custom function for saving an 'employee' object"""
        vals = {
            'name': self.name,
            'email': self.email,
            'tel_one': self.tel_one,
            'tel_two': self.tel_two,
            'cpf': self.cpf,
            'address': self.address,
            'cep': self.cep,
            'status': self.status,
            'pis_pasep': self.pis_pasep,
            'rg': self.rg,
            'cart_trabalho': self.cart_trabalho,
        }

        self.env['employee'].write(vals)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Sucesso"),
                'type': 'success',
                'message': _('Dados salvos com sucesso!'),
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                }
            },
        }

    @api.constrains('cpf')
    def _validate_cpf(self):
        """Checks size of the CPF variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.cpf:
                if len(rec.cpf) != 11:
                    raise ValidationError(_("O campo 'CPF' está com o tamanho incorreto. "
                                            "Precisa de 11 dígitos."))
                if not (rec.cpf).isnumeric():
                    raise ValidationError(_("O campo 'CPF' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))
                if self._validate_cpf_digits(rec.cpf) is False:
                    raise ValidationError(_("O 'CPF' é inválido."))

    @api.constrains('cep')
    def _validate_cep(self):
        """Checks size of the CEP variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.cep:
                if len(rec.cep) != 8:
                    raise ValidationError(_("O campo 'CEP' está está com o tamanho incorreto. "
                                            "Precisa de 8 dígitos"))
                if not (rec.cep).isnumeric():
                    raise ValidationError(_("O campo 'CEP' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

    @api.constrains('pis_pasep')
    def _validate_pis_pasep(self):
        """Checks size of the PIS-PASEP variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.pis_pasep:
                if len(rec.pis_pasep) != 11:
                    raise ValidationError(_("O campo 'PIS-PASEP' está com o tamanho incorreto. "
                                            "Precisa de 11 dígitos."))
                if not (rec.pis_pasep).isnumeric():
                    raise ValidationError(_("O campo 'PIS-PASEP' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))

    @api.constrains('rg')
    def _validate_rg(self):
        """Checks size of the RG variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.rg:
                if len(rec.rg) > 14 or len(rec.rg) < 6:
                    raise ValidationError(_("O campo 'RG' está com o tamanho incorreto. "
                                            "Ele possuí entre 6 e 14 dígitos."))
                if not (rec.rg).isnumeric():
                    raise ValidationError(_("O campo 'RG' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))

    @api.constrains('cart_trabalho')
    def _validate_cart_trabalho(self):
        """Checks size of the Carteira de Trabalho variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.cart_trabalho:
                if len(rec.cart_trabalho) != 11:
                    raise ValidationError(_("O campo 'Carteira de Trabalho' está com o tamanho incorreto. "
                                            "Precisa de 11 dígitos"))
                if not (rec.cart_trabalho).isnumeric():
                    raise ValidationError(_("O campo 'Carteira de Trabalho' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

    @api.constrains('tel_one')
    def _validate_tel_one(self):
        """Checks size of the 'tel_one' variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.tel_one:
                if len(rec.tel_one) != 11:
                    raise ValidationError(_("O campo 'Telefone 1' está com o tamanho incorreto. "
                                            "Precisa de 11 dígitos"))
                if not (rec.tel_one).isnumeric():
                    raise ValidationError(_("O campo 'Telefone 1' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

    @api.constrains('tel_two')
    def _validate_tel_two(self):
        """Checks size of the PIS-PASEP variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.tel_two:
                if len(rec.tel_two) != 11:
                    raise ValidationError(_("O campo 'Telefone 2' está com o tamanho incorreto."
                                            "Precisa de 11 dígitos"))
                if not (rec.tel_two).isnumeric():
                    raise ValidationError(_("O campo 'Telefone 2' contém carácteres inválidos."
                                            "O campo deve conter apenas números"))
    
    @api.constrains('email')
    def _validate_email(self):
        """Checks the validity of the
        email in the record"""
        for rec in self:
            if rec.email:
                if re.fullmatch(regex_email, rec.email) == None:
                    raise ValidationError(_("O formato do campo 'Email' é inválido."))

    _sql_constraints = [
        ('cpf_employee_unique', 'UNIQUE(cpf)', 'Já existe um \'Funcionário\' com esse \'CPF\'.')
    ]
    