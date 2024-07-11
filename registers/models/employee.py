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
    address = fields.Char(string='Endereço', required=False)
    cep = fields.Char(string='CEP', required=False)
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
