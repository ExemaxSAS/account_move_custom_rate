from odoo import api, fields, models, SUPERUSER_ID
from odoo.exceptions import AccessError, UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, values):
        res = super(AccountMove, self).write(values)
        self.manual_rate()
        return res

    def create(self, values):
        res = super(AccountMove, self).create(values)
        self.manual_rate()
        return res

    @api.depends('currency_id')
    def _get_currency_rate(self):
        for record in self:
            rate = 1
            if record.es_manual_rate==False:
                if record.currency_id.rate > 0:
                    if record.currency_id.name != 'ARS':
                        rate = 1 / record.currency_id.rate
                    else:
                        rate = 1
                    record.currency_rate = rate

    def manual_rate(self):
        for line in self.line_ids:
            if self.es_manual_rate == True:
                if line.debit != 0:
                    line.debit = line.amount_currency * self.currency_rate
                if line.credit != 0:
                    line.credit = line.amount_currency * self.currency_rate

    def _check_balanced(self):
            for rec in self:
                if rec.move_type == 'in_invoice' or rec.move_type == 'in_refund' or rec.move_type == 'entry':
                    if rec.es_manual_rate==True:
                            return True
            res = super(AccountMove, self)._check_balanced()
            return res

    currency_rate = fields.Float(string='Tasa de cambio', readonly=False ,compute='_get_currency_rate', store=True)
    es_manual_rate = fields.Boolean(string='Usar TC manual')
