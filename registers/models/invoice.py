# pylint: disable=undefined-loop-variable, protected-access line-too-long, pointless-statement
"""This are the invoice template and it's associated functions"""
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz

class Invoice(models.Model):
    """Fields and functions for the invoice record"""

# Generative functions  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _generate_register_date(self):
        """Function to generate current date based on user timezone"""
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        date_today = pytz.utc.localize(datetime.now()).astimezone(user_tz)
        return date_today.date()

    def _generate_installment_list(self, a):
        installment_list = []
        installment_list.append(('0', 'Não Possui'))

        for r in range(1, a+1):
            installment_list.append((str(r), str(r)))
        return installment_list

# Model variables -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _name = "invoice"
    _description = "Registro de  a Receitas."
    _rec_name = "display_name"

    id_invoice = fields.Char(string='Código', required=False)
    fiscal_note = fields.Char(string='Nota Fiscal', required=False)
    installment = fields.Selection(selection=lambda self: self._generate_installment_list(48),
                                   string='Parcela', required=True, default='0')
    invoice_type = fields.Selection([('fatura-contrato', 'Contrato'),
                                     ('venda-veiculo', 'Venda de Veículo'),
                                     ('juros-recebidos', 'Juros Recebidos'),
                                     ('credito-emprestio', 'Crédito de Empréstimos'),
                                     ('receita-aluguel', 'Receitas com Aluguel'),
                                     ('comissao', 'Comissão de Venda'),
                                     ('devolucao-credito', 'Devolução de Crédito'),
                                     ('outro', 'Outro')],
                                     string='Tipo de Conta', required=True)
    register_date = fields.Date(string='Data de Registro', default=_generate_register_date)
    invoice_file = fields.Binary(string='PDF da Conta', attachment=True)
    description = fields.Text(string='Descrição', required=False)
    value = fields.Float(string='Valor', required=True)
    origin = fields.Selection([('funcionario', 'Funcionário'), ('cliente', 'Cliente'),
                               ('outro', 'Outro')], string='Fonte', required=True,
                               default='outro')
    invoice_status = fields.Selection([('0', 'Provisória'), ('1', 'Autorizada'), ('2', 'Faturada'),
                                    ], string='Status da Conta', default='0')
    status_value = fields.Char(string='Descrição de Status', compute='_compute_status_value')
    signature = fields.Binary(string='Assinatura', required=True)
    external_cost_center_id = fields.Many2one(comodel_name='cost_center', string='Centro de Custo')
    external_contract_id = fields.Many2one(comodel_name='contract', string='Contrato')
    external_operation_id = fields.Many2one(comodel_name='operation', string='Operação de Caixa')
    external_employee_id = fields.Many2one(comodel_name='employee', string='Funcionário')
    external_client_id = fields.Many2one(comodel_name='client', string='Cliente')
    external_client_type = fields.Char(string='Tipo de Cliente', compute='_compute_client_type')
    cpf = fields.Char(string='CPF', compute='_compute_cpf')
    cnpj = fields.Char(string='CNPJ', compute='_compute_cnpj')
    filename = fields.Char()
    display_name = fields.Char(compute='_compute_display_name')

    pdf_view_status = fields.Integer(default=0)

# Main create function  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def create_invoice(self):
        """This is the custom function for saving a 'invoice' record"""
        if self.origin == "funcionario":
            self.write({'external_client_id': [(3, self.external_client_id.id)]})
        elif self.origin == "cliente":
            self.write({'external_employee_id': [(3, self.external_employee_id.id)]})
        else:
            self.write({'external_employee_id': [(3, self.external_employee_id.id)]})
            self.write({'external_client_id': [(3, self.external_client_id.id)]})

        if self.invoice_type != 'contract':
            self.write({'external_contract_id': [(3, self.external_contract_id.id)]})

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
            'cpf': self.cpf,
            'cnpj': self.cnpj,
            'external_contract_id': self.external_contract_id,
            'external_operation_id': self.external_operation_id,
            'external_employee_id': self.external_employee_id,
            'external_client_id': self.external_client_id,
            'external_client_type': self.external_client_type,
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

# Auxiliary functions - -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

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
                'message': _('Conta foi autorizada!'),
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                }
            },
        }

    def update_pdf_view(self):
        """Edits .xml so that the .pdf file is either expanded
        or reduced in visualization"""
        if self.pdf_view_status == 0:
            self.pdf_view_status = 1
        elif self.pdf_view_status == 1:
            self.pdf_view_status = 0

# Model constraints -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

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

    @api.constrains('fiscal_note')
    def _validate_rg(self):
        """Checks size of the fiscal_note variable to
        checks for non-numeric characters"""
        for rec in self:
            if rec.fiscal_note:
                if not (rec.fiscal_note).isnumeric():
                    raise ValidationError(_("O campo 'Nota Fiscal' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))

    @api.constrains('invoice_file')
    def _check_invoice_file(self):
        """Checks if the binary file is a '.pdf' file"""
        if self.filename:
            if str(self.filename.split(".")[1]) != 'pdf' :
                raise ValidationError("O sistema aceita apenas arquivos '.pdf'.")

    def _check_external_operation_id(self):
        for rec in self:
            if rec.external_operation_id:
                if rec.external_operation_id.is_editable is not True:
                    raise ValidationError(_("O caixa desta data não está editável."))
                if rec.external_operation_id.operation_status == '0':
                    raise ValidationError(_("O caixa está fechado."))

    _sql_constraints = [
        ('id_invoice_installment_unique', 'UNIQUE(id_invoice, installment)',
        'Já existe uma \'Conta a Receber\' com essa \'Parcela\' registrada ou'
        'outra conta com esse código.')
    ]

# Computed functions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _compute_display_name(self):
        """Function to generate specific name for any given record from
        this model"""
        for record in self:
            if not record.external_operation_id:
                if record.installment != '0':
                    record.display_name =f"{record.invoice_type}-parcela-{record.installment}"
                else:
                    record.display_name = f"{record.invoice_type}"
            else:
                if record.installment != '0':
                    record.display_name = f"{record.invoice_type}-parcela-{record.installment}-{record.external_operation_id.display_name}"
                else:
                    record.display_name = f"{record.invoice_type}-{record.external_operation_id.display_name}"

    def _compute_status_value(self):
        for rec in self:
            if rec.invoice_status == '0':
                self.status_value = 'Provisória'
            elif rec.invoice_status == '1':
                self.status_value = 'Autorizada'
            elif rec.invoice_status == '2':
                self.status_value = 'Faturada.'

    def _compute_cpf(self):
        for rec in self:
            if rec.external_employee_id:
                rec.cpf = rec.external_employee_id.cpf
            elif rec.external_client_id and rec.external_client_id.client_type == 'pessoa-fisica':
                rec.cpf = rec.external_client_id.cpf
            else:
                rec.cpf = False

    def _compute_cnpj(self):
        for rec in self:
            if rec.external_client_id and rec.external_client_id.client_type == 'pessoa-juridica':
                rec.cnpj = rec.external_client_id.cnpj
            else:
                rec.cnpj = False

    def _compute_client_type(self):
        for rec in self:
            if rec.external_client_id:
                if rec.external_client_id.client_type == 'pessoa-juridica':
                    rec.external_client_type = rec.external_client_id.client_type
                elif rec.external_client_id.client_type == 'pessoa-fisica':
                    rec.external_client_type == rec.external_client_id.client_type
            else:
                rec.external_client_type = False
