"""This are the client template and it's associated functions"""
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

regex_email = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9]+(\.[A-Z|a-z]{2,})+')

class Client(models.Model):
    """Fields and functions for the client object"""

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

# Model variables -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _name = "client"
    _description = "Registro de Clientes."

    name = fields.Char(string='Nome do Cliente', required=True)
    client_type = fields.Selection(selection=[('pessoa-fisica', 'Pessoa Física'),
                                              ('pessoa-juridica', 'Pessoa Jurídica'),
                                              ], string='Tipo de Cliente',
                                              required=True, default='pessoa-fisica')
    pf_type = fields.Selection(selection=[('nacional', 'Nacional'),
                                          ('estrangeiro', 'Estrangeiro'),
                                        ], string='Nacionalidade', required=False)
    pj_type = fields.Selection(selection=[('privado', 'Privado'),
                                          ('publico', 'Publico'),
                                        ], string='PJ', required=False)
    tel_one = fields.Char(string='Telefone', required=True)
    email = fields.Char(string='Email', required=False)
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
    address_complement = fields.Char(string='Complemento do Endereço', required=True)
    cpf = fields.Char(string='CPF', required=False)
    rg = fields.Char(string='RG', required=False)
    cnpj = fields.Char(string='CNPJ', required=False)
    foreign_doc = fields.Char(string='Documento Estrangeiro', required=False)
    contact_name = fields.Char(string='Nome do Contato', required=False)
    contact_tel = fields.Char(string='Telefone do Contato', required=False)
    contact_email = fields.Char(string='Email do Contato', required=False)
    city_name = fields.Char(string='Prefeitura', required=False)
    city_department = fields.Char(string='Secretaria', required=False)

    def create_client(self):
        """This is the custom function for saving an 'client' object"""

        if self.client_type == 'pessoa-fisica':
            self.cnpj = False
            self.pj_type = False
        elif self.client_type == 'pessoa-juridica':
            self.cpf = False
            self.rg = False
            self.pf_type = False

        if self.pf_type:
            if self.pf_type == 'estrangeiro':
                self.cpf = False
            elif self.pf_type == 'nacional':
                self.foreign_doc = False

        vals = {
            'name': self.name,
            'client_type': self.client_type,
            'tel_one': self.tel_one,
            'email': self.email,
            'address_state': self.address_state,
            'address_city': self.address_city,
            'address_complement': self.address_complement,
            'cpf': self.cpf,
            'rg': self.rg,
            'cnpj': self.cnpj,
            'foreign_doc': self.foreign_doc,
            'pf_type': self.pf_type,
            'contact_name': self.contact_name,
            'contact_tel': self.contact_tel,
            'contact_email': self.contact_email,
            'city_name': self.city_name,
            'city_department':self.city_department,
        }

        self.env['client'].write(vals)

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

# Model constraints -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @api.constrains('email')
    def _validate_email(self):
        """Checks the validity of the
        email in the record"""
        for rec in self:
            if rec.email:
                if re.fullmatch(regex_email, rec.email) is None:
                    raise ValidationError(_("O formato do campo 'Email' é inválido."))

    @api.constrains('tel_one')
    def _validate_tel_one(self):
        """Checks size of the 'tel_one' variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.tel_one:
                if len(rec.tel_one) != 11:
                    raise ValidationError(_("O campo 'Telefone' está com o tamanho incorreto. "
                                            "Precisa de 11 dígitos"))
                if not (rec.tel_one).isnumeric():
                    raise ValidationError(_("O campo 'Telefone' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

    @api.constrains('contact_email')
    def _validate_contact_email(self):
        """Checks the validity of the
        contact_email in the record"""
        for rec in self:
            if rec.contact_email:
                if re.fullmatch(regex_email, rec.contact_email) is None:
                    raise ValidationError(_("'O formato do campo 'Email do Contato' é inválido."))

    @api.constrains('contact_tel')
    def _validate_contact_tel(self):
        """Checks size of the 'contact_tel' variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.contact_tel:
                if len(rec.contact_tel) != 11:
                    raise ValidationError(_("O campo 'Telefone do Contato' está com o tamanho"
                                            "incorreto. "
                                            "Precisa de 11 dígitos"))
                if not (rec.contact_tel).isnumeric():
                    raise ValidationError(_("O campo 'Telefone do Contato' contém carácteres"
                                            "inválidos. "
                                            "O campo deve conter apenas números"))

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
