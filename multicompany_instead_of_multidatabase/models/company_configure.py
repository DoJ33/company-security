from odoo import models

"""
Is this useful?
from odoo.tools import populate
See base/populate/res_company.py res_partner.py res_user.py
"""

class CompanyConfigure(models.AbstractModel):
    _name = 'company.configure'
    _description = 'Set initial records on a new company'

    def _configure(self, companies):
        for company in companies:
            self = self.with_user(
                self.env.user.browse(2) # Administrator, not SUPERUSER
            ).with_context(
                active_test=False,
                allowed_company_ids=[company.id],
            )
            self.env.company = company
            self.env.companies = company

            # First
            company_json = dict(company.json or {})
            if not 'xmlid' in company_json:
                company_json['xmlid'] = {}

            # Main
            company_json = self._set_mail_channel_all_employees(company_json)

            # Last
            company.json = {}
            company.json = company_json

    def _set_mail_channel_all_employees(self, company_json):
        group_user_id = self.env.ref('base.group_user').id
        mail_channel_all_employees = self._insert_first_record(
            'mail.channel',
            [('group_ids', 'in', [group_user_id])],
            {
                'name': 'general',
                'description': 'General announcements for all employees.',
                'group_ids': [(4, group_user_id), 0],
            })
        if mail_channel_all_employees:
            # set is_pinned for mail.channel.partner
            company_json['xmlid']['mail.channel_all_employees'] = 'mail.channel,{}'.format(mail_channel_all_employees.id)
        return company_json

    def _insert_first_record(self, model, domain, values, copy=False, add_company_id=False):
        return self._try_insert_first_record(model, domain, values, copy)

    def _try_insert_first_record(self, model, domain, values, copy=False):
        '''
        model (string): the model to insert the first record
        domain (list):  the search domain to see if a record already exists
        values (dict):  values to insert into the first record
        copy (string):  optional external reference or 'model,res_id' of an existing record to 'copy' (otherwise 'create')
        '''
        records = self._env(model).search(domain)
        if not records.exists():
            if copy == False:
                record = self._env(model).create(values)
                return record
            elif ',' in copy:
                model, res_id = copy.split(',')
                record = self._env(model).sudo().browse(int(res_id)).copy(values)
                return record
            else:
                record = self._ref(copy).sudo().copy(values)
                return record
        else:
            record_count = self._env(model).with_context(active_test=False).search_count(domain)
            if record_count == 1:
                return records # Other variables might be dependent on the record

    def _env(self, model):
        try:
            return self.env[model]
        except KeyError:
            return self

    def _ref(self, xmlid):
        try:
            return self.env.ref(xmlid)
        except ValueError:
            return self

    def browse(self, *args, **kwargs):
        return self

    def copy(self, *args, **kwargs):
        pass

    def create(self, *args, **kwargs):
        pass

    def search(self, *args, **kwargs):
        return self
