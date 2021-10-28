# Copyright 2021 AppsToGROW - Henrik Norlin
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
            'name': 'base_company_security',
            'summary': 'Patch, Create database, Install',

            'author': 'AppsToGROW',
            'category': 'Administration',
            'data': [
                'security/ir.model.access.csv',
                'security/security.xml',
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
git am /path/to/extid-with-company_id.patch
git am /path/to/users-company_dependent-partner.patch
            ''',
}