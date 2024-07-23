"""This are the service template and it's associated functions"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class service(models.Model):
    """Fields and functions for the service object"""
    _name = "service"
    _description = "Registro de Centro de Custo."

    id_service = fields.Char(string='Código', required=True)
    type = fields.Char(string='Tipo', required=False)
    name = fields.Char(string='Nome', required=True)
    about = fields.Text(string='Descrição', required=False)

    def create_service(self):
        """This is the custom function for saving an 'service' object"""
        vals = {
            'id_service': self.id_service,
            'type': self.type,
            'name': self.name,
            'about': self.about,
        }

        self.env['service'].write(vals)

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

    @api.constrains('id_service')
    def _validate_renavan(self):
        """Checks size of the 'id_service' variable
        for non-numeric characters"""
        for rec in self:
            if not (rec.id_service).isnumeric():
                raise ValidationError(_("O campo 'ID' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))
