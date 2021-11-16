from odoo import api, fields, models


class Base(models.AbstractModel):
    _inherit = 'base'

    company_id = fields.Many2one('res.company', string='Company', store=True, index=True, default=lambda self: self.env.company)
