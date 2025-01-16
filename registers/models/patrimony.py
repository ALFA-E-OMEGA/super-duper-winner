# pylint: disable=undefined-loop-variable
"""This is the file for the 'patrimony' object"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class Patrimony(models.Model):
    """This are the fields and functions for the 'patrimony' object"""

# Generative functions  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _generate_tuple_list(self, a):
        tuple_list = []
        tuple_list.append(('0', 'Não Possui'))

        for r in range(1, a+1):
            tuple_list.append((str(r), str(r)))
        return tuple_list

# Model variables -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _name = "patrimony"
    _description = "Registro de patrimônio."
    _rec_name = "display_name"

    id_patrimony = fields.Char(string='Código', required=True)

    fuel_type = fields.Char(string='Combustível', required=False)

    vehicle_maker = fields.Char(string='Marca', required=False)
    vehicle_model = fields.Char(string='Modelo', required=False)

    classification = fields.Selection([('veiculo', 'Veículo'),
                                        ('pesado', 'Veículo Pesado'),
                                        ('outro', 'Outro')
                                        ], string = 'Classificação', required=True,
                                        default='outro')

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
                                    ], string='Tipo de Equipamento', required=False)

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
                                    ], string="Número de Equipamento")

    acquisition_date = fields.Date(string='Data de Aquisição', required=False)

    patrimony_file = fields.Binary(string='PDF do Patrimônio', attachment=True)
    filename = fields.Char()
    external_contract_id = fields.Many2one(comodel_name='contract', string='Contrato Original')
    contract_ids = fields.Many2many('contract', 'contract_patrimony_rel_table',
                                    string='Contratos')
    bill_ids = fields.One2many('bill', 'external_patrimony_id',  string="Contas a Pagar")
    display_name = fields.Char(compute='_compute_display_name')
    value = fields.Float(string='Valor do Patrimônio')

    pdf_view_status = fields.Integer(default=0)

# Onchange functions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @api.onchange('vehicle_plate')
    def set_upper_plate(self): 
        if self.vehicle_plate:   
            self.vehicle_plate = str(self.vehicle_plate).upper()   
        else:
            self.vehicle_plate = False
        return

# Auxiliary functions - -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def update_pdf_view(self):
        """Edits .xml so that the .pdf file is either expanded
        or reduced in visualization"""
        if self.pdf_view_status == 0:
            self.pdf_view_status = 1
        elif self.pdf_view_status == 1:
            self.pdf_view_status = 0

# Main create function  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def create_patrimony(self):
        """This is the custom function for saving an 'patrimony' object,
        clearing fields that are not going to be saves"""

        if self.classification == 'outro':
            self.renavan = False
            self.heavy_number = False
            self.heavy_type = False
            self.vehicle_type = False
        elif self.classification == 'veiculo':
            self.heavy_number = False
            self.heavy_type = False
        elif self.classification == 'pesado':
            self.renavan = False
            self.vehicle_type = False
            self.vehicle_plate = False

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
            'heavy_number': self.heavy_number,
            'external_contract_id': self.external_contract_id,
            'value': self.value,
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

# Model constraints  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

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

    @api.constrains('vehicle_plate')
    def _validate_vehicle_plate(self):
        """Checks size of the 'vehicle_plate' variable to limit different lengths"""
        for rec in self:
            if rec.vehicle_plate and self.classification == 'vehicles':
                if len(rec.vehicle_plate) != 7:
                    raise ValidationError(_("O campo 'Placa do Veículo' está com o tamanho"
                                            "incorreto. Precisa de 7 dígitos"))
                if not (rec.vehicle_plate).isalnum():
                    raise ValidationError(_("O campo 'Placa do Veículo' contém caracteres"
                                            " inválidos. "
                                            "O campo deve conter apenas letras e números."))

    @api.constrains('value')
    def _validate_value(self):
        """Checks if value field is a negative number or zero"""
        for rec in self:
            if rec.value <= 0:
                raise ValidationError(_("O campo 'valor' precisa ser maior que zero"))

    _sql_constraints = [
        ('id_patrimony_unique', 'UNIQUE(id_patrimony)',
        'Já existe um \'Patrimônio\' com esse \'Código\'.')
    ]

# Computed functions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _compute_display_name(self):
        """Function to generate specific name for any given record from
        this model"""
        for record in self:
            if record.classification == 'veiculo':
                record.display_name = f"{record.vehicle_plate}"
            if record.classification == 'pesado':
                record.display_name = f"{record.heavy_type}-{record.heavy_number}"
            else:
                record.display_name = f"{record.id_patrimony}"
