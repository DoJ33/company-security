# Copyright 2021 AppsToGROW - Henrik Norlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Copyight
# https://gist.github.com/danmana/5242f37b7d63daf4698de7c61c8b59fc#file-json_field-js
# https://www.odoo.com/forum/help-1/best-way-to-show-json-data-on-odoo-ui-171100
# Check the last link; I have asked if the person would like to make an Odoo module out of this.

{
            'name': 'multicompany_strict_security',
            'summary': 'Patch, Create database, Install',

            'author': 'AppsToGROW',
            'category': 'Administration',
            'data': [
                'security/ir.model.access.csv',
                'security/security.xml',
                'views/json_field.xml',
                'views/views.xml',
            ],
            'depends': [
                'base',
            ],
            'license': 'AGPL-3',
            'pre_init_hook': '_pre_init_hook',
            'uninstall_hook': '_WARNING_DELETE_RULES_uninstall_hook',
            'version': '14.0.1.0.0',
            'website': 'http://www.appstogrow.co',

            'description': '''
APPLY PATCHES
cd /path/to/odoo-server
git apply /path/to/multicompany_strict_security/patches/*


TODO:

When changing res.user company_id, the partner is also changing company_id! Should not change.

Restrict so a specific partner can only belong to one user.

Create one mail.channel per company, and define in res.company.json. (Done, but in the wrong company)
Method self.env.ref('mail.channel_all_employees') should return the json value.

It seems that JSON doesn't replace old values with new values...

Create new company: Add id to URL cids to avoid access error.
(This doesn't work: self.env.companies = new_company # The new environment "stops" in the api.py call_kw_model_create.)
            ''',
}
