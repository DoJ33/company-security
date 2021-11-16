from psycopg2 import sql
from odoo import api, SUPERUSER_ID
from openupgradelib import openupgrade
from .models.company_security import EXTID_MODULE_NAME

def _WARNING_DELETE_RULES_uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    rules = env['ir.rule'].search([('name','ilike','#%')])
    rules.unlink()
    ext_ids = env['ir.model.data'].search([('module','=',EXTID_MODULE_NAME),('name','ilike','%_rule')])
    ext_ids.unlink()

def _pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _create_initial_company_id_fields(env)
    # _pre_convert_to_company_dependent_user_partner(cr)


def _create_initial_company_id_fields(env):
    field_spec = [
        ('company_id', 'ir.rule', False, 'many2one', 'int4', EXTID_MODULE_NAME, 1),
        ('company_id', 'ir.model', False, 'many2one', 'int4', EXTID_MODULE_NAME, 1),
        ('company_id', 'ir.model.fields', False, 'many2one', 'int4', EXTID_MODULE_NAME, 1),
        ('company_id', 'res.lang', False, 'many2one', 'int4', EXTID_MODULE_NAME, 1),
    ]
    openupgrade.add_fields(env, field_spec)

# def _pre_convert_to_company_dependent_user_partner(cr):
#     openupgrade.rename_fields([('res.users', 'res_users', 'partner_id', 'temp_partner_id')])

# def _post_init_hook(cr, registry):
#     _post_convert_to_company_dependent_user_partner(cr)

# def _post_convert_to_company_dependent_user_partner(cr):
#     cr.execute("SELECT id FROM ir_model_fields "
#                "WHERE name='partner_id' AND model='res.users'")
#     fields_id = cr.fetchone()[0]
#     openupgrade.logged_query(
#         cr,
#         sql.SQL("""
#             INSERT INTO ir_property (
#                 fields_id, company_id, name, type, res_id, user_id, value_reference, partner_id
#             )
#             SELECT
#                 {fields_id}, company_id,
#                 'temp_partner_id', 'many2one',
#                 'res.users,' || id::TEXT, id,
#                 'res.partner,' || temp_partner_id::TEXT, partner_id
#             FROM res_users
#             WHERE partner_id IS NOT NULL
#             AND company_id IS NOT NULL;
#         """).format(fields_id=sql.Identifier(str(fields_id)))
#     )
#     openupgrade.drop_columns([('res_users', 'temp_partner_id')]) # How to drop the whole field?


