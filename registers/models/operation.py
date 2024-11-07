"""This are the operation template and it's associated functions"""
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz

class Operation(models.Model):
    """Fields and functions for the operation object"""
    _name = "operation"
    _description = "Registro de Caixa."
    _rec_name = "operation_date"

    def _generate_register_date(self):
        """Function to generate current date based on user timezone"""
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        date_today = pytz.utc.localize(datetime.now()).astimezone(user_tz)
        return date_today.date()
        
    operation_date = fields.Date(string='Data de Registro', default=_generate_register_date)
    operation_status = fields.Selection([('1', 'Aberto'), ('0', 'Fechado')],
                                       string="Status de Caixa", required=True,
                                       default='1')
    reopen_reason = fields.Text(string='Razão de Reabertura', required=False)
    is_editable = fields.Boolean(string='Editável', required=True, compute='compute_is_editable',
                                 default=True) 
    invoice_ids = fields.One2many('invoice', 'external_operation_id',  string="Contas a Receber")
    bill_ids = fields.One2many('bill', 'external_operation_id',  string="Contas a Pagar")

    def create_operation(self):
        """This is the custom function for saving an 'operation' object"""
        vals = {
            'operation_date': self.operation_date,
            'operation_status': self.operation_status,
            'reopen_reason': self.reopen_reason,
            'is_editable': self.is_editable,
            'bill_ids': self.bill_ids,
            }

        self.env['operation'].write(vals)
    
    def close_operation(self):
        """This function closes the operation status and locks editing the file"""
        self.operation_status = '0'

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
    
    def compute_is_editable(self):
        """Function only allows altering the operation in it's current date"""
        current_date = self._generate_register_date()
        for rec in self:
            if rec.operation_date == current_date:
                rec.is_editable = True
            else:
                rec.is_editable = False

    _sql_constraints = [
        ('operation_date_unique', 'UNIQUE(operation_date)',
         'Já existe um \'Caixa\' nesta \'Data\'.')
    ]

