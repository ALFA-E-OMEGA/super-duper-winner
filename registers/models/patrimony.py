"""This is the file for the 'patrimony' object"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Patrimony(models.Model):
    """This are the fields and functions for the 'patrimony' object"""
    _name = "patrimony"
    _description = "Registro de patrimônio."

    name = fields.Char(string='Nome', required=True)


    description = fields.Char(string='Descrição', required=False)

    classification = fields.Selection([('vehicles', 'Veículos'),
                                        ('heavies', 'Equipamento Pesado'),
                                        ('others', 'Outros')
                                        ], string = 'Classificação', required=True)

    vehicle_plate = fields.Char(string='Placa do Veículo', required=False)

    renavan = fields.Char(string='Renavan', required=False)

    heavy_type = fields.Selection([('escavadeira', 'Escavadeira'),
                                   ('retro_escavadeira', 'Retro Escavadeira'),
                                   ('pa_mecanica', 'Pá Mecânica'),
                                   ('triturador_galhos', 'Triturador de Galhos'),
                                   ('s90', 'S90'),
                                    ], string='pesado_type', required=False)

    heavy_number = fields.Selection([('1', 'Número 1'),
                                     ('2', 'Número 2'),
                                     ('3', 'Número 3'),
                                     ('4', 'Número 4'),
                                     ('5', 'Número 5'),
                                     ('6', 'Número 6'),
                                     ('7', 'Número 7'),
                                     ('8', 'Número 8'),
                                     ('9', 'Número 9'),
                                     ('10', 'Número 10'),
                                    ], string="pesado_num")

    def create_patrimony(self):
        """This is the custom function for saving an 'patrimony' object,
        clearing fields that are not going to be saves"""

        if self.classification == 'others':
            self.renavan = ''
            self.heavy_number = ''
            self.heavy_type = ''
            self.vehicle_plate = ''
        elif self.classification == 'vehciles':
            self.heavy_number = ''
            self.heavy_type = ''
        elif self.classification == 'heavies':
            self.renavan = ''
            self.vehicle_plate = ''

        vals = {
            'name': self.name,
            'description': self.description,
            'classification': self.classification,
            'vehicle_plate': self.vehicle_plate,
            'renavan': self.renavan,
            'heavy_type': self.heavy_type,
            'heavy_number': self.heavy_number
        }

        self.env['patrimony'].write(vals)

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

    @api.constrains('renavan')
    def _validate_renavan(self):
        """Checks size of the Renavan variable to limit different lengths
        and checks for non-numeric characters"""
        for rec in self:
            if rec.renavan and self.classification == 'vehicles':
                if len(rec.renavan) != 9:
                    raise ValidationError(_("O campo 'Renavan' está com o tamanho incorreto. "
                                            "Precisa de 9 dígitos"))
                if not (rec.renavan).isnumeric():
                    raise ValidationError(_("O campo 'Renavan' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))
