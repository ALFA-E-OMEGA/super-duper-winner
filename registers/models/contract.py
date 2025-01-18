# pylint: disable=undefined-loop-variable, wrong-import-order, line-too-long, protected-access, super-with-arguments, no-else-raise
"""This are the contract template and it's associated functions"""
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class Contract(models.Model):
    """Fields and functions for the contract object"""

# Generative functions  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _default_current_date(self):
        return fields.Date.context_today(self)

    def _generate_installment_list(self, a):
        installment_list = []

        for r in range(1, a+1):
            installment_list.append((str(r), str(r)))
        return installment_list

# Model variables -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    _name = "contract"
    _description = "Registro de Contrato."
    _inherit = ["mail.thread"]
    _rec_name = "display_name"

    id_contract = fields.Char(string='Código', required=True)
    register_date = fields.Date(string='Data de Registro', default=_default_current_date)
    contract_date = fields.Date(string='Data do Contrato', required=True)
    installments = fields.Selection(selection=lambda self: self._generate_installment_list(48),
                                   string='Parcela', required=True, default='1')
    status = fields.Selection([('ativo', 'Ativo'), ('inativo', 'Inativo'),
                               ('faturado', 'Faturado')],
                              string='Status', required=True, tracking=True)
    display_name = fields.Char(compute='_compute_display_name')
    external_client_id = fields.Many2one(comodel_name='client', string='Cliente', required=True)
    external_cost_center_id = fields.Many2one(comodel_name='cost_center', string='Centro de Custo')
    invoice_ids = fields.One2many('invoice', 'external_contract_id',  string="Receitas")
    bill_ids = fields.One2many('bill', 'external_contract_id',  string="Despesas")
    patrimony_ids = fields.Many2many('patrimony', 'contract_patrimony_rel_table',
                                     string='Patrimônios')

# Main create function  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def create_contract(self):
        """This is the custom function for saving an 'contract' object"""
        vals = {
            'id_contract': self.id_contract,
            'register_date': self.register_date,
            'contract_date': self.contract_date,
            'installments': self.installments,
            'status': self.status,
            'external_client_id': self.external_client_id,
            'external_cost_center_id': self.external_cost_center_id,
            'invoice_ids': self.invoice_ids,
            'bill_ids': self.bill_ids,
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

# Main delete function  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def unlink(self):
        """Custom unlink function for 'contract' module"""
        for rec in self:
            if len(rec.invoice_ids) > 0:
                raise UserError(_("Contratos com 1 ou mais parcelas não podem "
                                "deletados"))
            else:
                return super(Contract, self).unlink()

# Model constraints  -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    @api.constrains('id_contract')
    def _validate_id_contract(self):
        """Checks size of the 'id_contract' variable
        for non-numeric characters"""
        for rec in self:
            if not (rec.id_contract).isnumeric():
                raise ValidationError(_("O campo 'ID' contém carácteres inválidos. "
                                            "O campo deve conter apenas números."))

    @api.constrains('status')
    def _validate_status(self):
        """Checks if the contract is ready for 'faturado'
        status"""
        for rec in self:
            if rec.status == 'faturado' and len(rec.invoice_ids) != int(rec.installments):
                raise ValidationError(_("O contrato ainda não tem o número de "
                                        "parcelas total.\n" +
                                        str(len(rec.invoice_ids)) + "/" + rec.installments))


    _sql_constraints = [
        ('id_contract_unique', 'UNIQUE(id_contract)', 'Já existe um \'Contrato\' com esse \'ID\'.')
    ]

# Computed functions -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

    def _compute_display_name(self):
        """Function to generate specific name for any given record from
        this model"""
        for record in self:
            record.display_name = f"{record.id_contract} | {record.external_client_id.name} | {record.contract_date}"
