"""This are the employee template and it's associated functions"""
# pylint: skip-file
from odoo import api, models, fields, _
from odoo.exceptions import ValidationError

class Employee(models.Model):
    """Fields and functions for the employee object"""
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
                                            "Precisa de 11 dígitos"))
                if not (rec.cpf).isnumeric():
                    raise ValidationError(_("O campo 'CPF' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

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
                                            "Precisa de 11 dígitos"))
                if not (rec.pis_pasep).isnumeric():
                    raise ValidationError(_("O campo 'PIS-PASEP' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

    @api.constrains('rg')
    def _validate_rg(self):
        """Checks size of the RG variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.rg:
                if len(rec.rg) != 9:
                    raise ValidationError(_("O campo 'RG' está com o tamanho incorreto. "
                                            "Precisa de 9 dígitos"))
                if not (rec.rg).isnumeric():
                    raise ValidationError(_("O campo 'RG' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

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

