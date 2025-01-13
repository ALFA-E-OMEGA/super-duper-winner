# pylint: disable=undefined-loop-variable, protected-access, line-too-long, pointless-statement
"""This are the bill template and it's associated functions"""
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz

class Bill(models.Model):
    """Fields and functions for the bill object"""

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

    _name = "bill"
    _description = "Registro de Contas a Pagar."
    _rec_name = "display_name"

    id_bill = fields.Char(string='Código', required=False)
    fiscal_note = fields.Char(string='Nota Fiscal', required=False)
    installment = fields.Selection(selection=lambda self: self._generate_installment_list(48),
                                   string='Parcela', required=True, default='0')
    bill_type = fields.Selection([('manutencao-veiculo', 'Manutenção de Veículo'),
                                  ('manutencao-pesado', 'Manutenção de Veículo Pesado'),
                                  ('combustivel', 'Combustível'), ('ipva', 'IPVA'),
                                  ('lubrificante', 'Óleos e Lubrificantes'),
                                  ('material-obra', 'Material de Obra'),
                                  ('telefone', 'Telefone'), ('gratificacao', 'Gratificação'),
                                  ('internet', 'Internet'), ('condominio', 'Condomínio'),
                                  ('luz', 'Luz'), ('ensino', 'Ensino'),
                                  ('gas', 'Gáz'), ('cartorio', 'Cartório'),
                                  ('frete', 'Frete'), ('aluguel', 'Aluguel'),
                                  ('correio', 'Correio'), ('consorcio', 'Consórcio'),
                                  ('cartao-credito', 'Cartão de Crédtio'),
                                  ('maquinas-equipamentos', 'Máquinas e Equipamentos'),
                                  ('servico-terceiro-pf', 'Serviços Terceiros PF'),
                                  ('servico-terceiro-pj', 'Serviços Terceiros PJ'),
                                  ('locacao-veiculo', 'Locação de Veículo'),
                                  ('tributo', 'Tributos'), ('salario', 'Salário'),
                                  ('alimentacao', 'Alimentação'), ('seguro', 'Seguro'),
                                  ('emprestimo-bancario', 'Empréstimo Bancário'),
                                  ('vale-adiantamento', 'Adiantamento de Salário'),
                                  ('multa', 'Multas de Trânsito'), ('fgts', 'FGTS'),
                                  ('grt', 'Licenciamento Anual (GRT)'),
                                  ('pensao-alimenticia', 'Pensão Alimentícia'),
                                  ('adiantamento', 'Adiantamentos'),
                                  ('material-escritorio', 'Material de Escritório'),
                                  ('financiamento', 'Financiamento de Veículo'),
                                  ('taxa', 'Taxas e Emolumentos'),
                                  ('outro', 'Outro')],
                                  string='Tipo de Conta', required=True, default='outro')
    register_date = fields.Date(string='Data de Registro', default=_generate_register_date)
    bill_file = fields.Binary(string='PDF da Conta', attachment=True)
    validation_date = fields.Date(string='Data de Vencimento', required=True)
    description = fields.Text(string='Descrição', required=False)
    value = fields.Float(string='Valor', required=True)
    origin = fields.Selection([('funcionario', 'Funcionário'), ('cliente', 'Cliente'),
                               ('outro', 'Outro')], string='Fonte', required=True,
                               default='outro')
    bill_status = fields.Selection([('0', 'Provisória'), ('1', 'Autorizada'), ('2', 'Paga'),
                                    ], string='Status da Conta', default='0')
    status_value = fields.Char(string='Descrição de Status', compute='_compute_status_value')
    signature = fields.Binary(string='Assinatura', required=True)
    external_cost_center_id = fields.Many2one(comodel_name='cost_center', string='Centro de Custo')
    external_patrimony_id = fields.Many2one(comodel_name='patrimony', string='Patrimônio')
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

    def create_bill(self):
        """This is the custom function for saving a 'bill' record"""
        if self.origin == "funcionario":
            self.write({'external_client_id': [(3, self.external_client_id.id)]})
        elif self.origin == "cliente":
            self.write({'external_employee_id': [(3, self.external_employee_id.id)]})
        else:
            self.write({'external_employee_id': [(3, self.external_employee_id.id)]})
            self.write({'external_client_id': [(3, self.external_client_id.id)]})

        if self.bill_type not in ('manutencao-veiculo', 'manutencao-pesado'):
            if self.external_patrimony_id:
                self.write({'external_patrimony_id': [(3, self.external_patrimony_id.id)]})

        vals = {
            'bill_id': self.id_bill,
            'installment': self.installment,
            'fiscal_note': self.fiscal_note,
            'bill_type': self.bill_type,
            'register_date': self.register_date,
            'bill_file': self.bill_file,
            'validation_date': self.validation_date,
            'description': self.description,
            'value': self.value,
            'origin': self.origin,
            'bill_status': self.bill_status,
            'external_cost_center_id': self.external_cost_center_id,
            'cpf': self.cpf,
            'cnpj': self.cnpj,
            'external_patrimony_id': self.external_patrimony_id,
            'external_operation_id': self.external_cost_center_id,
            'external_employee_id': self.external_employee_id,
            'external_client_id': self.external_client_id,
            'external_client_type': self.external_client_type,
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

# Auxiliary functions - -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def update_bill_status(self):
        """This function changes the bill status and locks editing the file"""
        if self.bill_status == '0':
            self.bill_status = '1'
        elif self.bill_status == '1':
            self.bill_status = '2'

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

    @api.constrains('id_bill')
    def _validate_rg(self):
        """Checks size of the id_bill variable to
        checks for non-numeric characters"""
        for rec in self:
            if rec.id_bill:
                if not (rec.id_bill).isnumeric():
                    raise ValidationError(_("O campo 'Código' contém carácteres inválidos. "
                                            "O campo deve conter apenas números"))

    @api.constrains('value')
    def _validate_value(self):
        """Checks if value field is a negative number or zero"""
        for rec in self:
            if rec.value <= 0:
                raise ValidationError(_("O campo 'valor' precisa ser igual ou maior que zero."))

    @api.constrains('fiscal_note')
    def _validate_rg(self):
        """Checks size of the fiscal_note variable to
        checks for non-numeric characters"""
        for rec in self:
            if rec.fiscal_note:
                if not (rec.fiscal_note).isnumeric():
                    raise ValidationError(_("O campo 'Nota Fiscal' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))

    @api.constrains('bill_file')
    def _check_bill_file(self):
        """Checks if the binary file is a '.pdf' file"""
        if self.filename:
            if str(self.filename.split(".")[1]) != 'pdf' :
                raise ValidationError("O sistema aceita apenas arquivos '.pdf'.")

    @api.constrains('validation_date')
    def _check_validation_date(self):
        """Checks if 'validation_date' is not invalid"""
        if self.validation_date:
            if self.validation_date < self.register_date:
                raise ValidationError(_("A 'Data de Validade' é inválida. "
                                        "Ela não pode ser mais antiga que a data de regsitro."))

    @api.constrains('external_operation_id')
    def _check_external_operation_id(self):
        for rec in self:
            if rec.external_operation_id:
                if rec.external_operation_id.is_editable is not True:
                    raise ValidationError(_("O caixa desta data não está editável."))
                if rec.external_operation_id.operation_status == '0':
                    raise ValidationError(_("O caixa está fechado."))

    _sql_constraints = [
        ('id_bill_installment_unique', 'UNIQUE(id_bill, installment)',
        'Já existe uma \'Conta a Pagar\' com essa \'Parcela\' registrada ou'
        'outra conta com esse código.')
    ]

# Computed functions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _compute_display_name(self):
        """Function to generate specific name for any given record from
        this model"""
        for record in self:
            if not record.external_operation_id:
                if record.installment != '0':
                    record.display_name = f"{record.bill_type}-parcela-{record.installment}"
                else:
                    record.display_name = f"{record.bill_type}"
            else:
                if record.installment != '0':
                    record.display_name = f"{record.bill_type}-parcela-{record.installment}-{record.external_operation_id.display_name}"
                else:
                    record.display_name = f"{record.bill_type}-{record.external_operation_id.display_name}"

    def _compute_status_value(self):
        for rec in self:
            if rec.bill_status == '0':
                self.status_value = 'Provisória'
            elif rec.bill_status == '1':
                self.status_value = 'Autorizada'
            elif rec.bill_status == '2':
                self.status_value = 'Paga'

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
