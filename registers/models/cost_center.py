"""This are the cost_center template and it's associated functions"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class cost_center(models.Model):
    """Fields and functions for the cost_center object"""
    _name = "cost_center"
    _description = "Registro de Centro de Custo."

    id_cost_center = fields.Char(string='Código', required=True)
    name = fields.Char(string='Nome', required=True)
    about = fields.Text(string='Descrição', required=False)

    def create_cost_center(self):
        """This is the custom function for saving an 'cost_center' object"""
        vals = {
            'id_cost_center': self.id_cost_center,
            'name': self.name,
            'about': self.about,
        }

        self.env['cost_center'].write(vals)

    @api.constrains('id_cost_center')
    def _validate_renavan(self):
        """Checks size of the 'id_cost_center' variable
        for non-numeric characters"""
        for rec in self:
            if not (rec.id_cost_center).isnumeric():
                raise ValidationError(_("O campo 'Centro de Custo' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))

