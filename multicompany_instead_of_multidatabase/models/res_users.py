from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)

import odoo.sql_db


class Users(models.Model):
    _inherit = 'res.users'

    @api.model
    def create(self, vals):
        vals = self._remove_admin_access(vals)
        return super(Users, self).create(vals)

    def write(self, vals):
        vals = self._remove_admin_access(vals)
        if 'partner_id' in vals or ('name' in vals and 'lang' in vals):
            vals = self._set_partner(vals)
        return super(Users, self).write(vals)

    def _remove_admin_access(self, vals):
        admin_access = "sel_groups_{erp}_{system}".format(
            erp=str(self.env.ref('base.group_erp_manager').id),
            system=str(self.env.ref('base.group_system').id),
        )
        vals.pop(admin_access, None)
        return vals

    def _set_partner(self, vals):
        users = self
        for user in users:
            if not user.partner_id:
                if len(users) > 1:
                    raise UserError("You cannot update multiple users when not all users have a related partner for the company.")
                vals = user._create_partner(vals)
                user.flush()
        if 'partner_id' in vals and vals['partner_id']:
            if len(users) > 1:
                raise UserError("You cannot update multiple users with the same partner.")
        return vals

    def _create_partner(self, vals):
        self.ensure_one()
        partner = self.env['res.partner'].create({
            'name': vals['name'],
            'lang': vals['lang'],
        })
        vals.pop('name')
        vals.pop('lang')
        vals['partner_id'] = partner
        return vals
