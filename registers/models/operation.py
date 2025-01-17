"""This are the operation template and it's associated functions"""
from datetime import datetime
from odoo import models, fields, _
from odoo.exceptions import ValidationError
import pytz

class Operation(models.Model):
    """Fields and functions for the operation object"""

# Generative functions  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _generate_register_date(self):
        """Function to generate current date based on user timezone"""
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        date_today = pytz.utc.localize(datetime.now()).astimezone(user_tz)
        return date_today.date()

# Model variables -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _name = "operation"
    _description = "Registro de Caixa."
    _rec_name = "operation_date"

    operation_date = fields.Date(string='Data de Registro', default=_generate_register_date)
    operation_status = fields.Selection([('1', 'Aberto'), ('0', 'Fechado')],
                                       string="Status de Caixa", required=True,
                                       default='1')
    reopen_reason = fields.Text(string='Razão de Reabertura', required=False)
    is_editable = fields.Boolean(string='Editável', required=True, compute='_compute_is_editable',
                                 default=True, store=True)
    is_closed = fields.Boolean(string='Fechado', required=True, compute='_compute_is_closed',
                                 default=False, store=True)
    is_reopen = fields.Boolean(string='Foi Reaberto', required=False, default=False)
    invoice_ids = fields.One2many('invoice', 'external_operation_id',  string="Contas a Receber")
    bill_ids = fields.One2many('bill', 'external_operation_id',  string="Contas a Pagar")
    revenues_sum = fields.Float(string='Lucro Total', compute='_compute_revenues_sum')
    expenses_sum = fields.Float(string='Despesa Total', compute='_compute_expenses_sum')
    total_profit = fields.Float(string='Lucro Total', default=0.0)
    total_profit_positive = fields.Boolean(string='Lucro', defaut=True)

# Main create function  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def create_operation(self):
        """This is the custom function for saving an 'operation' object"""

        if self.is_reopen is True:
            return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Erro"),
                'type': 'danger',
                'message': _('Um caixa reaberto precisa de uma razão.'),
                'sticky': False,
            },
        }

        vals = {
            'operation_date': self.operation_date,
            'operation_status': self.operation_status,
            'reopen_reason': self.reopen_reason,
            'is_editable': self.is_editable,
            'is_reopen': self.is_reopen,
            'revenues_sum': self.revenues_sum,
            'expenses_sum': self.expenses_sum,
            'total_profit': self.total_profit,
            'total_profit_positive': self.total_profit_positive,
            }

        self.env['operation'].write(vals)

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

    def close_operation(self):
        """This function closes the operation status and locks editing the file"""

        if self.is_reopen is True:
            if self.reopen_reason:
                if len(self.reopen_reason) < 6:
                    raise ValidationError(_('Uma conta reaberta precisa de um motivo'
                                            ' para a reabertura.')) 
            else:
                raise ValidationError(_('Uma conta reaberta precisa de um motivo'
                                            ' para a reabertura.'))

        self.operation_status = '0'
        for rec in self:
            for bill in rec.bill_ids:
                if bill.bill_status == '1':
                    bill.bill_status = '2'

            for invoice in rec.invoice_ids:
                if invoice.invoice_status == '1':
                    invoice.invoice_status = '2'

            rec.total_profit = rec.revenues_sum - rec.expenses_sum

            if rec.total_profit >= 0:
                rec.total_profit_positive = True
            else:
                rec.total_profit_positive = False

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Sucesso"),
                'type': 'success',
                'message': _('Caixa fechado com sucesso!'),
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                }
            },
        }

    def reopen_operation(self):
        """This function re-opens the operation and updates the 'Reason' field to true"""
        self.operation_status = '1'
        self.is_reopen = True

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Sucesso"),
                'type': 'success',
                'message': _('Caixa reaberto com sucesso!'),
                'sticky': False,
                'next': {
                    'type': 'ir.actions.act_window_close',
                }
            },
        }

# Model constraints  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _sql_constraints = [
        ('operation_date_unique', 'UNIQUE(operation_date)',
         'Já existe um \'Caixa\' nesta \'Data\'.')
    ]

# Computed functions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _compute_is_editable(self):
        """Function only allows altering the operation in it's current date"""
        current_date = self._generate_register_date()
        for rec in self:
            if rec.operation_date == current_date:
                rec.is_editable = True
            else:
                rec.is_editable = False

    def _compute_revenues_sum(self):
        """Function to calculate revenue and remove 'Provisória' invoices"""
        for rec in self:
            total_revenue = 0.0
            for invoice in rec.invoice_ids:
                if invoice.invoice_status == '0':
                    self.write({'invoice_ids': [(3, invoice.id)]})
                else:
                    revenue = invoice.value
                    total_revenue += revenue
            rec.revenues_sum = total_revenue

    def _compute_expenses_sum(self):
        """Function to calculate revenue and remove 'Provisória' bills"""
        for rec in self:
            total_expense = 0.0
            for bill in rec.bill_ids:
                if bill.bill_status == '0':
                    self.write({'bill_ids': [(3, bill.id)]})
                else:
                    expense = bill.value
                    total_expense += expense
            rec.expenses_sum = total_expense
