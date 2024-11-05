"""This are the operation template and it's associated functions"""
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import pytz

class Operation(models.Model):
    """Fields and functions for the operation object"""
    _name = "operation"
    _description = "Registro de Caixa."

    def _generate_register_date(self):
        """Function to generate current date based on user timezone"""
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        date_today = pytz.utc.localize(datetime.now()).astimezone(user_tz)
        return date_today.date()

    def _generate_id_operation(self):
        current_date = self._generate_register_date()
        
        num_of_records = self.env['operation'].search_count([('operation_date', '=', current_date)])

        if num_of_records == 0:
            return 'Abertura'
        elif num_of_records == 1:  
            return   'Reabertura'
        else:
            return 'Operação Inválida'
        
    operation_date = fields.Date(string='Data de Registro', default=_generate_register_date)
    id_operation = fields.Char(string='Operação', required=True, default=_generate_id_operation)

    def create_operation(self):
        """This is the custom function for saving an 'operation' object"""
        vals = {
            'operation_date': self.operation_date,
            'id_operation': self.id_operation,
            }

        self.env['operation'].write(vals)


    @api.constrains('id_operation')
    def _validate_id_operation(self):
        for rec in self:
            if rec.id_operation == 'Operação Inválida':
                raise ValidationError(_("O sistema permite apenas 2 operações de caixa por dia."))

