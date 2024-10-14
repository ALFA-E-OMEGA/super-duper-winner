"""This are the bill template and it's associated functions"""
from uuid import uuid4
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz

class Bill(models.Model):
    """Fields and functions for the bill object"""


    def _generate_bill_id(self):
        """Function to generate an ID for the bill object"""
        return uuid4().node

    def _generate_register_date(self):
        """Function to generate current date based on user timezone"""
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        date_today = pytz.utc.localize(datetime.now()).astimezone(user_tz)
        return date_today.date()

    _name = "bill"
    _description = "Registro de Contas."

    bill_id = fields.Char(string='ID Conta', default=_generate_bill_id)
    register_date = fields.Date(string='Data de Registro', default=_generate_register_date)
    bill_file = fields.Binary(string='PDF da Conta', attachment=True)
    validation_date = fields.Date(string='Data de Vencimento', required=True)
    description = fields.Char(string='Descrição', required=False)
    value = fields.Float(string='Valor', required=True)
    origin = fields.Selection([('is_cpf', 'Funcionário'), ('is_cnpj', 'Fornecedor'),
                               ('other', 'Outro')], string='Fonte', required=True,
                               default='other')
    bill_status = fields.Char(string='Status da Conta', default='Provisória')
    signature = fields.Binary(string='Assinatura', required=True)
    cost_center_id = fields.Many2one(comodel_name='cost_center', string='Centro de Custo')
    name = fields.Char(string='Nome', required=False)
    cpf = fields.Char(string='CPF', required=False)
    cnpj = fields.Char(string='CNPJ', required=False)
    filename = fields.Char()

    def create_bill(self):
        """This is the custom function for saving a 'bill' object"""
        if self.origin == "is_cpf":
            self.cnpj = ''
        elif self.origin == "is_cnpj":
            self.cpf = ''
        else:
            self.cpf = ''
            self.cnpj = ''
            self.name = ''

        vals = {
            'bill_id': self.bill_id,
            'register_date': self.register_date,
            'bill_file': self.bill_file,
            'validation_date': self.validation_date,
            'description': self.description,
            'value': self.value,
            'origin': self.origin,
            'bill_status': self.bill_status,
            'cost_center_id': self.cost_center_id,
            'name': self.name,
            'cpf': self.cpf,
            'cnpj': self.cnpj,
        }

        self.env['bill'].write(vals)

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

    def update_bill_status(self):
        """This function changes the bill status and locks editing the file"""
        if self.bill_status == 'Provisória':
            self.bill_status = 'Autorizada'
        elif self.bill_status == 'Autorizada':
            self.bill_status = 'Paga'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Sucesso"),
                'type': 'success',
                'message': _('Status atualizado para ' + self.bill_status + '!'),
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                }
            },
        }


    @api.constrains('value')
    def _validate_value(self):
        """Checks if value field is a negative number or zero"""
        for rec in self:
            if rec.value <= 0:
                raise ValidationError(_("O campo 'valor' precisa ser igual ou maior que zero"))

    @api.constrains('cpf')
    def _validate_cpf(self):
        """Checks size of the CPF variable to limit different lengths"""
        for rec in self:
            if rec.cpf and self.origin == "is_cpf":
                if len(rec.cpf) != 1:
                    raise ValidationError(_("O campo 'CPF' está com o tamanho incorreto. "
                                            "Precisa de 11 dígitos"))
                if not (rec.cpf).isnumeric():
                    raise ValidationError(_("O campo 'CPF' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

    @api.constrains('cnpj')
    def _validate_cnpj(self):
        """Checks size of the CPNJ variable to limit different lengths"""
        for rec in self:
            if rec.cnpj and self.origin == "is_cnpj":
                if len(rec.cnpj) != 14:
                    raise ValidationError(_("O campo 'CNPJ' está está com o tamanho incorreto. "
                                                "Precisa de 8 dígitos"))
                if not (rec.cnpj).isnumeric():
                    raise ValidationError(_("O campo 'CNPJ' contém carácteres inválidos. "
                                                "O campo deve conter apenas números"))

    @api.constrains('bill_file')
    def _check_file(self):
        """Checks if the binary file is a '.pdf' file"""
        if self.filename:
            if str(self.filename.split(".")[1]) != 'pdf' :
                raise ValidationError("O sistema aceita apenas arquivos '.pdf'.")
            
    @api.constrains('validation_date')
    def _check_validation_date(self):
        """Checks if 'validation_date' is not invalid"""
        if self.validation_date:
            if self.validation_date <= self.register_date:
                raise ValidationError(_("A 'Data de Validade' é inválida. "
                                        "Ela não pode ser mais antiga que a data de regsitro."))
