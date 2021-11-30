from odoo import api, fields, models


class Base(models.AbstractModel):
    _inherit = 'base'

    company_id = fields.Many2one('res.company', string='Company', store=True, index=True, default=lambda self: self.env.company)

    """
    Controllers may not know the company of a record.
    Use sudo() here rather than in each controller.
    """

    def with_my_company(self):
        return self.with_company(self.my_company())

    def my_company(self):
        company = self.sudo().mapped('company_id')
        assert len(company) == 1
        return company
