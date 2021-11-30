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
}
