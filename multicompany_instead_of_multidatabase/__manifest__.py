# Copyright 2021 AppsToGROW - Henrik Norlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

# Copyight
# https://gist.github.com/danmana/5242f37b7d63daf4698de7c61c8b59fc#file-json_field-js
# https://www.odoo.com/forum/help-1/best-way-to-show-json-data-on-odoo-ui-171100
# Check the last link; I have asked if the person would like to make an Odoo module out of this.

{
            'name': 'multicompany_instead_of_multidatabase',
            'summary': 'Patch, Create database, Install',

            'author': 'AppsToGROW',
            'category': 'Administration',
            'data': [
                'security/ir.model.access.csv',
                'security/security.xml',
                'views/ir.model.data.xml',
                'views/json_field.xml',
                'views/res.company.xml',
                'views/res.users.xml',
            ],
            'depends': [
                'base',
                'web', # web.assets_backend for json_field
            ],
            'license': 'AGPL-3',
            'pre_init_hook': '_pre_init_hook',
            'uninstall_hook': '_WARNING_DELETE_RULES_uninstall_hook',
            'version': '14.0.1.0.0',
            'website': 'http://www.appstogrow.co',

            'description': '''
APPLY PATCHES
cd /path/to/odoo-server
git apply /path/to/multicompany_instead_of_multidatabase/patches/*

Administrator (user id 2) is doing the configuration for companies.

SECURITY VULNERABILITIES

Users may run untrusted code in server actions, salary rules, tax rules etc.
core.patch has additional security for save_eval to forbid certain text phrases in the untrusted code.

If 'odoo.tools.safe_eval.wrap_module' exists in an Odoo module, a python module is whitelisted for safe_eval.
Check the security of the python module before using the Odoo module.

Below are some methods of the ORM. If they exist in an Odoo module, check the security of the code before using the module.
.with_company()
.with_context()
.with_env()
.with_prefetch()
.with_user()
.sudo()


TODO:

Not important for security:

*mail.channel form: warning access denied (ir.rule for mail.channel, username = partnername of company 1. Both if company_dependent partner exists or not.)

*Create new company: Add id to URL cids to avoid access error.
(This doesn't work: self.env.companies = new_company # The new environment "stops" in the api.py call_kw_model_create.)
            ''',
}
