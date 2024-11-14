# pylint: disable=undefined-loop-variable, protected-access
"""This are the invoice template and it's associated functions"""
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz

class Invoice(models.Model):
    """Fields and functions for the invoice record"""

    def _generate_register_date(self):
        """Function to generate current date based on user timezone"""
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        date_today = pytz.utc.localize(datetime.now()).astimezone(user_tz)
        return date_today.date()

    def _generate_installment_list(self, a):
        installment_list = []
        installment_list.append(('0', 'Não Possui'))

        for r in range(1, a+1):
            b = (r, r)
            installment_list.append(b)
        return installment_list

    _name = "invoice"
    _description = "Registro de Contas a Receber."

    id_invoice = fields.Char(string='Código', required=False)
    fiscal_note = fields.Char(string='Nota Fiscal', required=False)
    installment = fields.Selection(selection=lambda self: self._generate_installment_list(48),
                                   string='Parcela', required=True)
    invoice_type = fields.Selection([('contract', 'Contrato'),
                                  ('other', 'Outro')],
                                  string='Tipo de Conta', required=True)
    register_date = fields.Date(string='Data de Registro', default=_generate_register_date)
    invoice_file = fields.Binary(string='PDF da Conta', attachment=True)
    description = fields.Text(string='Descrição', required=False)
    value = fields.Float(string='Valor', required=True)
    origin = fields.Selection([('is_cpf', 'Funcionário'), ('is_cnpj', 'Fornecedor'),
                               ('other', 'Outro')], string='Fonte', required=True,
                               default='other')
    invoice_status = fields.Selection([('0', 'Provisória'), ('1', 'Faturada'),
                                       ],string='Status da Conta', default='0')
    status_value = fields.Char(string='Descrição de Status', compute='_compute_status_value')
    signature = fields.Binary(string='Assinatura', required=True)
    external_cost_center_id = fields.Many2one(comodel_name='cost_center', string='Centro de Custo')
    external_contract_id = fields.Many2one(comodel_name='contract', string='Contrato')
    external_operation_id = fields.Many2one(comodel_name='operation', string='Operação de Caixa')
    client_name = fields.Char(string='Nome', required=False)
    cpf = fields.Char(string='CPF', required=False)
    cnpj = fields.Char(string='CNPJ', required=False)
    filename = fields.Char()
    display_name = fields.Char(compute='_compute_display_name')
    is_clearable = fields.Boolean(string='Limpável', compute='_compute_is_clearable')

    pdf_view_status = fields.Integer(default=0)

    def update_pdf_view(self):
        """Edits .xml so that the .pdf file is either expanded
        or reduced in visualization"""
        if self.pdf_view_status == 0:
            self.pdf_view_status = 1
        elif self.pdf_view_status == 1:
            self.pdf_view_status = 0

    def clear_external_operation_id(self):
        """Removes the association between an 'external_operation_id'
        and a 'invoice' record"""
        if self.external_operation_id:
            self.external_operation_id = False

    def create_invoice(self):
        """This is the custom function for saving a 'invoice' record"""
        if self.origin == "is_cpf":
            self.cnpj = ''
        elif self.origin == "is_cnpj":
            self.cpf = ''
        else:
            self.cpf = ''
            self.cnpj = ''
            self.client_name = ''

        if self.invoice_type != 'contract':
            self.external_contract_id = ''

        vals = {
            'id_invoice': self.id_invoice,
            'installment': self.installment,
            'fiscal_note': self.fiscal_note,
            'invoice_type': self.invoice_type,
            'register_date': self.register_date,
            'invoice_file': self.invoice_file,
            'description': self.description,
            'value': self.value,
            'origin': self.origin,
            'invoice_status': self.invoice_status,
            'external_cost_center_id': self.external_cost_center_id,
            'client_name': self.client_name,
            'cpf': self.cpf,
            'cnpj': self.cnpj,
            'external_contract_id': self.external_contract_id,
            'external_opration_id': self.external_operation_id,
            'name':self.display_name,
            'is_clearable': self.is_clearable,
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
        if self.invoice_status == '0':
            self.invoice_status = '1'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Sucesso"),
                'type': 'success',
                'message': _('Status atualizado para \'' + self.status_value + '\'!'),
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
                name = record.id_invoice + '-parcela-' + record.installment
            else:
                name = record.id_invoice + '-parcela-unica'
        record.display_name = name
    
    def _compute_is_clearable(self):
        """Disables removing association if the 'external_operation_id' is
        no longer editable"""
        for rec in self:
            if rec.external_operation_id:
                rec.is_clearable = rec.external_operation_id.is_editable
            else:
                rec.is_clearable = False
    
    def _compute_status_value(self):
        for rec in self:
            if rec.bill_status == '0':
                self.status_value = 'Faturada'
