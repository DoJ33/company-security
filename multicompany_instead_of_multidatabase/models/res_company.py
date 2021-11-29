from odoo import api, fields, models
import psycopg2


class JsonField(fields.Field):
    """
    Represents a postgresql Json column (JSON values are mapped to the Python equivalent type of list/dict).
    """
    type = 'json'  # Odoo type of the field (string)
    column_type = ('json', 'json')  # database column type (ident, spec)

    def convert_to_column(self, value, record, values=None, validate=True):
        """ Convert ``value`` from the ``write`` format to the SQL format. """
        # By default the psycopg2 driver does not know how to map dict/list to postgresql json types
        # We need to convert it to the right db type when inserting in the db
        # see https://www.psycopg.org/docs/extras.html
        if value is None:
            return None
        else:
            return psycopg2.extras.Json(value)


class Company(models.Model):
    _inherit = 'res.company'

    json = JsonField(default={"xmlid":{}})

    @api.model
    def create(self, vals):
        old_company = self.env.company
        new_company = super(Company, self.sudo()).create(vals)
        new_company.sudo().partner_id.write({'company_id': new_company.id})
        self.env['company.configure']._configure(new_company)
        return new_company

    def configure(self):
        companies = self
        self.env['company.configure']._configure(companies)
