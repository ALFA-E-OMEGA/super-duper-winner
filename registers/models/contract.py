"""This are the contract template and it's associated functions"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
import pytz

class Contract(models.Model):
    """Fields and functions for the contract object"""

    def _generate_register_date(self):
        """Function to generate current date based on user timezone"""
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
        date_today = pytz.utc.localize(datetime.now()).astimezone(user_tz)
        return date_today.date()
    
    _name = "contract"
    _description = "Registro de Contrato."

    id_contract = fields.Char(string='Código', required=True)
    register_date = fields.Date(string='Data de Registro', default=_generate_register_date)
    contract_date = fields.Date(string='Data do Contrato', required=True)
    status = fields.Selection([('ativo', 'Ativo'), ('inativo', 'Inativo')],
                              string='Status', required=True)
    client_type = fields.Selection([('estado', 'Estado'), ('cidade', 'Cidade'),
                                    ('prefeitura', 'Prefeitura'), ('secretaria', 'Secretaria')],
                                    string="Cliente", required=True)
    display_name = fields.Char(compute='_compute_display_name')

    def create_contract(self):
        """This is the custom function for saving an 'contract' object"""
        vals = {
            'id_contract': self.id_contract,
            'register_date': self.register_date,
            'contract_date': self.contract_date,
            'status': self.status,
            'client_type': self.client_type,
            'name': self.display_name,
        }

        self.env['contract'].write(vals)

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

    @api.constrains('id_contract')
    def _validate_id_contract(self):
        """Checks size of the 'id_contract' variable
        for non-numeric characters"""
        for rec in self:
            if not (rec.id_contract).isnumeric():
                raise ValidationError(_("O campo 'ID' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))
            
    def _compute_display_name(self):
        """Function to generate specific name for any given record from
        this model"""
        for record in self:
            name = record.client_type + '_' + record.id_contract

        record.display_name = name
            