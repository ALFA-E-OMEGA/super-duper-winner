from odoo import models, fields

class Patrimony(models.Model):
    _name = "patrimony"
    _description = "Registro de patrimônio."

    name = fields.Char(string='Nome', required=True)


    description = fields.Char(string='Descrição', required=False)

    classification = fields.Selection([('vehicles', 'Veículos'),
                                        ('heavies', 'Equipamento Pesado'),
                                        ('others', 'Outros')
                                        ], string = 'Classificação')

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

    def save(self):

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
        return {'type': 'ir.actions.act_window_close'}
