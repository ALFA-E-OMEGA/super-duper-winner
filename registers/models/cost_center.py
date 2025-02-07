# pylint: disable=line-too-long, super-with-arguments, no-else-raise
"""This are the cost_center template and it's associated functions"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class CostCenter(models.Model):
    """Fields and functions for the cost_center object"""

# Model variables -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _name = "cost_center"
    _description = "Registro de Centro de Custo."

    sequence = fields.Integer(string="Sequência", default=1)
    id_cost_center = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nome', required=True)
    about = fields.Text(string='Descrição', required=False)

# Main create function  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def create_cost_center(self):
        """This is the custom function for saving an 'cost_center' object"""
        vals = {
            'id_cost_center': self.id_cost_center,
            'name': self.name,
            'about': self.about,
        }

        self.env['cost_center'].write(vals)

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

# Main delete function  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def unlink(self):
        """Custom unlink function for 'cost_center' module"""
        bill_count=self.env['bill'].search_count([('external_cost_center_id','=', self.id)])
        invoice_count=self.env['invoice'].search_count([('external_cost_center_id','=', self.id)])
        contract_count=self.env['contract'].search_count([('external_cost_center_id','=', self.id)])
        if bill_count > 0 or invoice_count > 0 or contract_count > 0:
            raise UserError(_("Esse Centro de Custo tem despesas, "
                                "receitas ou contratos associados "
                                "e não pode ser excluído."))
        else:
            return super(CostCenter, self).unlink()

# Model constraints  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @api.constrains('id_cost_center')
    def _validate_id_cost_center(self):
        """Checks size of the 'id_cost_center' variable
        for non-numeric characters"""
        for rec in self:
            if not (rec.id_cost_center).isnumeric():
                raise ValidationError(_("O campo 'ID' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))

    _sql_constraints = [
        ('id_cost_center_unique', 'UNIQUE(id_cost_center)',
         'Já existe um \'Centro de Custo\' com esse \'Código\'.')
    ]
