"""This is the file for the 'patrimony' object"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Patrimony(models.Model):
    """This are the fields and functions for the 'patrimony' object"""
    _name = "patrimony"
    _description = "Registro de patrimônio."

    id_patrimony = fields.Char(string='Código', required=True)

    fuel_type = fields.Char(string='Combustível', required=True)

    vehicle_maker = fields.Char(string='Marca', required=False)
    vehicle_model = fields.Char(string='Modelo', required=False)

    classification = fields.Selection([('vehicles', 'Veículos'),
                                        ('heavies', 'Equipamento Pesado'),
                                        ('others', 'Outros')
                                        ], string = 'Classificação', required=True)

    vehicle_type = fields.Selection([('truck', 'Caminhão'),
                                     ('car', 'Carro')
                                     ], string = 'Tipo de Veículo', required=False)

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

    acquisition_date = fields.Date(string='Data de Aquisição', required=False)

    patrimony_file = fields.Binary(string='PDF do Patrimônio', attachment=True)
    filename = fields.Char()

    pdf_view_status = fields.Integer(default=0)

    def update_pdf_view(self):
        """Edits .xml so that the .pdf file is either expanded
        or reduced in visualization"""
        if self.pdf_view_status == 0:
            self.pdf_view_status = 1
        elif self.pdf_view_status == 1:
            self.pdf_view_status = 0

    def create_patrimony(self):
        """This is the custom function for saving an 'patrimony' object,
        clearing fields that are not going to be saves"""

        if self.classification == 'others':
            self.renavan = ''
            self.heavy_number = ''
            self.heavy_type = ''
            self.vehicle_plate = ''
            self.vehicle_type = ''
        elif self.classification == 'vehicles':
            self.heavy_number = ''
            self.heavy_type = ''
        elif self.classification == 'heavies':
            self.renavan = ''
            self.vehicle_plate = ''
            self.vehicle_type = ''

        vals = {
            'id_patrimony': self.id_patrimony,
            'fuel_type': self.fuel_type,
            'vehicle_maker': self.vehicle_maker,
            'vehicle_model': self.vehicle_model,
            'classification': self.classification,
            'vehicle_type': self.vehicle_type,
            'acquisition_date': self.acquisition_date,
            'vehicle_plate': self.vehicle_plate,
            'patrimony_file': self.patrimony_file,
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

    @api.constrains('id_patrimony')
    def _validate_id_patrimony(self):
        """Checks size of the 'id_patrimony' variable
        for non-numeric characters"""
        for rec in self:
            if not (rec.id_patrimony).isnumeric():
                raise ValidationError(_("O campo 'ID' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))

    @api.constrains('patrimony_file')
    def _check_patrimony_file(self):
        """Checks if the binary file is a '.pdf' file"""
        if self.filename:
            if str(self.filename.split(".")[1]) != 'pdf' :
                raise ValidationError("O sistema aceita apenas arquivos '.pdf'.")

    _sql_constraints = [
        ('id_patrimony_unique', 'UNIQUE(id_patrimony)',
        'Já existe um \'Patrimônio\' com esse \'Código\'.')
    ]
