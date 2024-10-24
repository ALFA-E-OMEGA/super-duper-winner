"""This are the invoice template and it's associated functions"""
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz

class Invoice(models.Model):
    """Fields and functions for the invoice object"""

    def _generate_register_date(self):
        """Function to generate current date based on user timezone"""
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        date_today = pytz.utc.localize(datetime.now()).astimezone(user_tz)
        return date_today.date()

    _name = "invoice"
    _description = "Registro de Contas a Receber."

    id_invoice = fields.Char(string='Código', required=False)
    fiscal_note = fields.Char(string='Código', required=False)
    installment = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'),
                                    ('4', '4'), ('5', '5'), ('6', '6'),
                                    ('7', '7'), ('8', '8'), ('9', '9'),
                                    ('10', '10'), ('0', 'Não Possui')],
                                    string='Parcela', required=True)
    invoice_type = fields.Selection([('maintenance', 'Manutenção'),
                                  ('contract', 'Contrato')],
                                  string='Tipo de Conta', required=True)
    register_date = fields.Date(string='Data de Registro', default=_generate_register_date)
    invoice_file = fields.Binary(string='PDF da Conta', attachment=True)
    receiving_date = fields.Date(string='Data de Recebimento', required=True)
    description = fields.Char(string='Descrição', required=False)
    value = fields.Float(string='Valor', required=True)
    origin = fields.Selection([('is_cpf', 'Funcionário'), ('is_cnpj', 'Fornecedor'),
                               ('other', 'Outro')], string='Fonte', required=True,
                               default='other')
    invoice_status = fields.Char(string='Status da Conta', default='Provisória')
    signature = fields.Binary(string='Assinatura', required=True)
    cost_center_id = fields.Many2one(comodel_name='cost_center', string='Centro de Custo')
    external_contract_id = fields.Many2one(comodel_name='contract', string='Contrato')
    client_name = fields.Char(string='Nome', required=False)
    cpf = fields.Char(string='CPF', required=False)
    cnpj = fields.Char(string='CNPJ', required=False)
    filename = fields.Char()
    display_name = fields.Char(compute='_compute_display_name')

    pdf_view_status = fields.Integer(default=0)

    def update_pdf_view(self):
        """Edits .xml so that the .pdf file is either expanded
        or reduced in visualization"""
        if self.pdf_view_status == 0:
            self.pdf_view_status = 1
        elif self.pdf_view_status == 1:
            self.pdf_view_status = 0

    def create_invoice(self):
        """This is the custom function for saving a 'invoice' object"""
        if self.origin == "is_cpf":
            self.cnpj = ''
        elif self.origin == "is_cnpj":
            self.cpf = ''
        else:
            self.cpf = ''
            self.cnpj = ''
            self.client_name = ''

        vals = {
            'id_invoice': self.id_invoice,
            'installment': self.installment,
            'fiscal_note': self.fiscal_note,
            'invoice_type': self.invoice_type,
            'register_date': self.register_date,
            'invoice_file': self.invoice_file,
            'receiveing_date': self.receiving_date,
            'description': self.description,
            'value': self.value,
            'origin': self.origin,
            'invoice_status': self.invoice_status,
            'cost_center_id': self.cost_center_id,
            'client_name': self.client_name,
            'cpf': self.cpf,
            'cnpj': self.cnpj,
            'external_contract_id': self.external_contract_id,
            'name':self.display_name,
        }

        self.env['invoice'].write(vals)

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

    def update_invoice_status(self):
        """This function changes the invoice status and locks editing the file"""
        if self.invoice_status == 'Provisória':
            self.invoice_status = 'Recebida'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Sucesso"),
                'type': 'success',
                'message': _('Status atualizado para ' + self.invoice_status + '!'),
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                }
            },
        }

    @api.constrains('id_invoice')
    def _validate_rg(self):
        """Checks size of the id_invoice variable to
        checks for non-numeric characters"""
        for rec in self:
            if rec.id_invoice:
                if not (rec.id_invoice).isnumeric():
                    raise ValidationError(_("O campo 'Código' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

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
                if len(rec.cpf) != 11:
                    raise ValidationError(_("O campo 'CPF' está com o tamanho incorreto. "
                                            "Precisa de 11 dígitos"))
                if not (rec.cpf).isnumeric():
                    raise ValidationError(_("O campo 'CPF' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))
    
    @api.constrains('fiscal_note')
    def _validate_rg(self):
        """Checks size of the fiscal_note variable to
        checks for non-numeric characters"""
        for rec in self:
            if rec.fiscal_note:
                if not (rec.fiscal_note).isnumeric():
                    raise ValidationError(_("O campo 'Nota Fiscal' contém carácteres inválidos. "
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

    @api.constrains('invoice_file')
    def _check_invoice_file(self):
        """Checks if the binary file is a '.pdf' file"""
        if self.filename:
            if str(self.filename.split(".")[1]) != 'pdf' :
                raise ValidationError("O sistema aceita apenas arquivos '.pdf'.")
            
    _sql_constraints = [
        ('id_invoice_installment_unique', 'UNIQUE(id_invoice, installment)',
        'Já existe uma \'Conta a Receber\' com essa \'Parcela\' registrada.')
    ]

    def _compute_display_name(self):
        """Function to generate specific name for any given record from
        this model"""
        for record in self:
            if record.installment != '0':
                name = record.id_invoice + '_parcela_' + record.installment
            else:
                name = record.id_invoice + '_parcela_unica'
        record.display_name = name