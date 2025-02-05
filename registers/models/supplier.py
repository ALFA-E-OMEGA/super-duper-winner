# pylint: disable=line-too-long,
"""This are the supplier template and it's associated functions"""
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

regex_email = re.compile(r'([A-Za-z0-9]{1,24}+[.-_])*[A-Za-z0-9]{0,18}+@[A-Za-z0-9]+(\.[A-Z|a-z]{2,12})+')

class Supplier(models.Model):
    """Fields and functions for the supplier object"""

# Model variables -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _name = "supplier"
    _description = "Registro de Fornecedor."

    sequence = fields.Integer(string='Sequência', default=1)
    supplier_area = fields.Char(string='Área de Fornecumento', required=False)
    name = fields.Char(string='Nome', required=True)
    cnpj = fields.Char(string='CNPJ', required=False)
    address_state = fields.Selection(selection=[('acre', 'AC'), ('alagoas', 'AL'),
                                                ('amapa', 'AP'), ('amazonas', 'AM'),
                                                ('bahia', 'BA'), ('ceara', 'CE'),
                                                ('espirito-santo', 'ES'), ('goias', 'GO'),
                                                ('maranhao', 'MA'), ('mato-grosso', 'MT'),
                                                ('mato-grosso-do-sul', 'MS'),
                                                ('minas-gerais', 'MG'),
                                                ('para', 'PA'), ('paraiba', 'PB'),
                                                ('parana', 'PR'), ('pernambuco', 'PE'),
                                                ('piaui', 'PI'), ('rio-de-janeiro', 'RJ'),
                                                ('rio-grande-do-norte', 'RN'),
                                                ('rio-grande-do-sul', 'RS'),
                                                ('rondonia', 'RO'), ('roraima', 'RR'),
                                                ('santa-catarina', 'SC'), ('sao-paulo', 'SO'),
                                                ('sergipe', 'SE'), ('tocantins', 'TO'),
                                                ('distrito-federal', 'DF')],
                                                string='Estado do Endereço',
                                                required=True, defaul='rio-de-janeiro')
    address_city = fields.Char(string='Cidade do Endereço', required=True)
    address_complement = fields.Char(string='Complemento do Endereço', required=False)
    email = fields.Char(string='Email', required=False)
    tel_one = fields.Char(string='Telefone 1', required=True)
    pix_key = fields.Char(string='Chave PIX', required=False)
    pix_key_type = fields.Selection(selection=[('type_cpf', 'CPF'),
                                               ('type_tel', 'Telefone')], string='Tipo de Chave PIX')

# Main create function  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def create_supplier(self):
        """This is the custom function for saving an 'supplier' object"""
        vals = {
            'name': self.name,
            'supplier_area': self.supplier_area,
            'address_state': self.address_state,
            'address_city': self.address_city,
            'address_complement': self.address_complement,
            'tel_one': self.tel_one,
            'email': self.email,
        }

        self.env['supplier'].write(vals)

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

# Model constraints  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @api.constrains('tel_one')
    def _validate_tel_one(self):
        """Checks size of the 'tel_one' variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.tel_one:
                if len(rec.tel_one) != 11:
                    raise ValidationError(_("O campo 'Telefone 1' está com o tamanho "
                                            "incorreto. Precisa de 11 dígitos."
                                            "\n 2 dígitos do "
                                            "DDD e 9 dígitos."))
                if not (rec.tel_one).isnumeric():
                    raise ValidationError(_("O campo 'Telefone 1' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))

    @api.constrains('email')
    def _validate_email(self):
        """Checks the validity of the
        email in the record"""
        for rec in self:
            if rec.email:
                if re.fullmatch(regex_email, rec.email) is None:
                    raise ValidationError(_("O formato do campo 'Email' é inválido. "
                                            "O correto é \'email@provedor.terminação\'"))

    @api.constrains('cnpj')
    def _validate_cnpj(self):
        """Checks size of the CPNJ variable to limit different lengths"""
        for rec in self:
            if rec.cnpj:
                if len(rec.cnpj) != 14:
                    raise ValidationError(_("O campo 'CNPJ' está está com o tamanho incorreto. "
                                                "Precisa de 14 dígitos."))
                if not (rec.cnpj).isnumeric():
                    raise ValidationError(_("O campo 'CNPJ' contém carácteres inválidos. "
                                                "O campo deve conter apenas números."))

    @api.constrains('pix_key')
    def _validate_pix_key(self):
        """Checks size of the 'pix_key' variable to limit different lengths"""
        for rec in self:
            if rec.pix_key:
                if len(rec.pix_key) != 11:
                    raise ValidationError(_("O campo 'Chave PIX' está está com o tamanho incorreto.\n "
                                                "Precisa de 11 dígitos."))
                if not (rec.pix_key).isnumeric():
                    raise ValidationError(_("O campo 'Chave PIX' contém carácteres inválidos.\n "
                                                "O campo deve conter apenas números."))

    _sql_constraints = [
        ('cnpj_supplier_unique', 'UNIQUE(cnpj)',
        'Já existe um \'Fornecedor\' com esse CNPJ.')
    ]
