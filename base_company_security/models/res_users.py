from odoo import models, fields, api, exceptions, SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)

import odoo.sql_db


class Users(models.Model):
    _inherit = 'res.users'

    ''' RESTRICT USERS SO THEY CANNOT GET ADMINISTRATION RIGHTS '''

    @api.model
    def create(self, vals):
        if self.env.user.id != SUPERUSER_ID:
            vals.pop(self._admin_access(), None)
        user = super(Users, self).create(vals)
        return user

    def write(self, vals):
        if self.env.user.id != SUPERUSER_ID:
            vals.pop(self._admin_access(), None)
        user = super(Users, self).write(vals)
        return user

    def _admin_access(self):
        return "sel_groups_" + str(self.env.ref('base.group_erp_manager').id) + "_" + str(self.env.ref('base.group_system').id)

    ''' CREATE COMPANY_DEPENDENT PARTNER '''

    def create_company_dependent_partner(self):
        pass
