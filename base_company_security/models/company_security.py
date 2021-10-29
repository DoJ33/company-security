import logging
from openupgradelib import openupgrade
import os

from odoo import models, fields, api, exceptions, SUPERUSER_ID
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

# Module name for external IDs made with python.
# (Not in XML, so cannot be a module name.)
# Used for company_id fields, also in hooks.py.
EXTID_MODULE_NAME = '__base_company_security__'

PUBLIC_MODELS = [
    'res.users',
    'website',
    'website.menu',
]

SYSTEM_COMPANY_MODELS = [
    'account.account.type',
    'ir.actions.act_url',
    'ir.actions.act_window',
    'ir.actions.act_window_close',
    'ir.actions.act_window.view',
    'ir.actions.actions',
    'ir.actions.client',
    'ir.actions.report',
    'ir.actions.server',
    'ir.actions.todo',
    'ir.attachment',
    'ir.filters',
    'ir.mail.server',
    'ir.model.data',
    'ir.translation',
    'ir.ui.menu',
    'ir.ui.view',
    'mail.template',
    'res.field',                    # https://github.com/apps2grow/apps/tree/14.0/base_field_value
    'res.field.selection_value',    # https://github.com/apps2grow/apps/tree/14.0/base_field_value
    'stock.location',
    'uom.uom',
]

SYSTEM_MODELS = [
    # BASE, IR, RES
    'base.language.export',
    'base.language.import',
    'base.language.install',
    'base.module.uninstall',
    'base.module.update',
    'base.module.upgrade',
    'base.update.translations',
    'base_import.import',
    'ir.cron',
    'ir.logging',
    'ir.model',
    'ir.model.access',
    'ir.model.constraint',
    'ir.model.fields',
    'ir.model.relation',
    'ir.module.category',
    'ir.module.module',
    'ir.module.module.dependency',
    'ir.module.module.exclusion',
    'ir.rule',
    'ir.server.object.lines',
    'res.bank',
    'res.config',
    'res.config.installer',
    'res.config.settings',
    'res.country',
    'res.country.state',
    'res.currency',
    'res.groups',
    'res.lang',
    'res.partner.industry',
    'res.request.link',
    # APPS
    'account.payment.method',
    'account.tax.group',
    'change.password.user',
    'change.password.wizard',
    'l10n_no_payroll.tabelltrekk',
    'mail.alias',
    'payment.icon',
    'report.layout',
    'report.paperformat',
    'uom.category',
    'web_tour.tour',
    'wizard.ir.model.menu.create',
]

NO_ACCESS_MODELS = [
    'ir.config_parameter',
]

# TODO: IRREGULAR_SQL_VIEW_NAMES = {
#     # 'view_name': 'model_name',
# }

# NEW, NOT TESTED #####################################################################################

SECURITY_RULES = {
    'PUBLIC_MODELS': {
        'read_if': 'allowed',
        'edit_if': 'allowed AND selected_company/parent/child',
    },
    # default
    'COMPANY_MODELS': {
        'read_if': 'allowed AND selected_company/parent/child',
        'edit_if': 'allowed AND selected_company/parent/child',
    },
    'SYSTEM_COMPANY_MODELS': {
        'read_if': 'system OR ( allowed AND selected_company/parent/child )',
        'edit_if': 'allowed AND selected_company/parent/child',
    },
    'SYSTEM_MODELS': {
        'read_if': 'system',
        'edit_if': 'system AND ( allowed AND selected_company )',
    },
    'NO_ACCESS_MODELS': {
        'read_if': 'system AND ( allowed AND selected_company )',
        'edit_if': 'system AND ( allowed AND selected_company )',
    },
}

SECURITY_DOMAIN_WORDS = {
    '(': 'BEGIN',
    ')': 'END',
    'AND': "&",
    'OR': "|",
    'allowed': "('{company_id}','in',company_ids)",
    'selected_company': "('{company_id}','=',company_id)",
    'selected_company/parent/child': "'|',('{company_id}','child_of',company_id),('{company_id}','parent_of',company_id)",
    'system': "('{company_id}','=',1)",
}

SECURITY_FIELDS = {
    'res.company': 'id',
    'res.users': 'company_ids',
    'default': 'company_id',
}

def _get_security_type(model_name):
    if model_name in PUBLIC_MODELS:
        return 'public'
    elif model_name in SYSTEM_COMPANY_MODELS:
        return 'system_company'
    elif model_name in SYSTEM_MODELS:
        return 'system'
    elif model_name in NO_ACCESS_MODELS:
        return 'no_access'
    else:
        return 'company'

def _assert_security_domain_words_and_order(words_list):
    type = ''
    last_type = ''
    parenthesis_counter = 0
    first = 0
    last = len(words_list) - 1
    for count, word in enumerate(words_list):
        assert word in SECURITY_DOMAIN_WORDS

        if word == '(':
            type = 'parenthesis'
            parenthesis_counter += 1
        elif word == ')':
            type = 'parenthesis'
            parenthesis_counter -= 1
        elif word in ('AND', 'OR'):
            type = 'operator'
        else:
            type = 'expression'

        assert parenthesis_counter >= 0
        assert type != last_type

        if count in (first, last):
            assert type in ('parenthesis', 'expression')

    # There should be max one operator type inside a parenthesis.
    # This assert is done in the _recursive_words2domain method.

def _recursive_words2domain(words_list):
    words_sub_list = []
    domain_list = []
    parenthesis_counter = 0
    operator = ''
    last_operator = ''
    for word in words_list:
        if word == '(':
            if parenthesis_counter > 0:
                words_sub_list.append(word)
            parenthesis_counter += 1
        elif word == ')':
            parenthesis_counter -= 1
            if parenthesis_counter > 0:
                words_sub_list.append(word)
            else:
                domain_list.extend(_recursive_words2domain(words_sub_list))
                last_operator = ''
        else:
            if word in ('AND', 'OR'):
                operator = word
                assert operator == last_operator or not last_operator
            words_sub_list.append(word)
    words_sub_dict = {}
    for count, word in enumerate(words_sub_dict):
        if count % 2 == 0:
            words_sub_dict[count+1] = word
        else:
            words_sub_dict[count-1] = word

    for count in range(0, len(words_sub_dict)):
        if count in words_sub_dict:
            domain_list.append(SECURITY_DOMAIN_WORDS[words_sub_dict[count]])
    return domain_list


class CompanySecurity(models.AbstractModel):
    _name = 'company.security'
    _description = 'Security between companies'

    # main methods

    def _register_hook(self):
        self._limit_access_to_system_models()
        self._set_global_security_rules_on_all_models_except_ir_rule()
        self._set_company_manager_access_and_rules()

    def _limit_access_to_system_models(self):
        pass

    def _set_global_security_rules_on_all_models_except_ir_rule(self):
        models = self['ir.models'].search([('model', '!=', 'ir.rule')])
        for model in models:
            security_type = _get_security_type(model._name)
            for do_if in SECURITY_RULES[security_type]:
                domain = self._words2domain(do_if)
                # values = rule_dictionary
                # self._set_security_rule(values)

    def _set_company_manager_access_and_rules(self):
        pass

    # low-level methods

    def _words2domain(self, words):
        words_list = words.split(' ')
        _assert_security_domain_words_and_order(words_list)
        domain_list = _recursive_words2domain(words_list)
        domain_draft = ', '.join(domain_list)

        domain = domain_draft.format(company_id='company_id')
        return domain


# OLD #####################################################################################

SECURITY_TYPES = [
    'company',
    'company_published',
    'public',
    'system',
    'system_company',
    'users',

    def _register_hook(self):
        self._protect_system_models()
        self._create_security_rules()
        self._update_company_manager_access_and_rules()

    def _protect_system_models(self):
        system_model_ids = self.env['ir.model'].search([('model', 'in', SYSTEM_MODELS)]).ids
        system_group_ids = (self.env.ref('base.group_erp_manager').id,self.env.ref('base.group_system').id)

        # Search for create/write/delete access for non-system users to system models
        #
        # ( group is empty OR not system ) AND ( write OR create OR unlink )
        # (        A       OR     B      ) AND (   C   OR    D   OR    E   )
        # [ '&', '|', (A), (B), '|', (C), '|', (D), (E) ]
        # https://www.odoo.com/forum/ayuda-1/domain-notation-using-multiple-and-nested-and-2170

        ir_model_access_domain = [
            ('model_id', 'in', system_model_ids),
            '&',
            '|', ('group_id','=', False), ('group_id.id','not in', system_group_ids),
            '|', ('perm_create', '=', True), '|', ('perm_write', '=', True), ('perm_unlink', '=', True)
        ]
        access_records = self.env['ir.model.access'].search(ir_model_access_domain)
        for record in access_records:
            record.write({'perm_create': False, 'perm_write': False, 'perm_unlink': False})
        access_records = self.env['ir.model.access'].search(ir_model_access_domain)
        if access_records:
            raise UserError('These records give access to system models: %s' % access_records)

    def _create_security_rules(self):
        values_for_rules = self._get_security_rules()
        for values in values_for_rules:
            values['perm_read'] = values.pop('read')
            values['perm_write'] = values.pop('write')
            values['perm_create'] = values.pop('create')
            values['perm_unlink'] = values.pop('unlink')
            values['domain_force'] = values.pop('domain')
            model = self.env['ir.model'].search([('model', '=', values['model'])])
            values['model_id'] = model.id
            del values['model']
            rule_type =  values.pop('type')
            # Create rule
            rule = self._set_rule_values(values)

            # Create external ID for the rule
            xmlid = '%s_%s_rule' % (
                model.model.replace('.','_'),
                rule_type,
            )
            xmlid_record = self.env['ir.model.data'].search([('module','=',EXTID_MODULE_NAME), ('name','=',xmlid)])
            if xmlid_record:
                xmlid_record.write({'res_id': rule.id})
            else:
                openupgrade.add_xmlid(
                    self.env.cr,
                    EXTID_MODULE_NAME,
                    xmlid,
                    'ir.rule',
                    rule.id,
                )
        self._set_company_id_to_1_where_null()

    def _update_company_manager_access_and_rules(self):
        Rule = self.env['ir.rule']
        Access = self.env['ir.model.access']
        company_manager_group = self.env.ref('base_company_security.group_company_manager')
        models = [m for m in
                  self.env['ir.model'].search([('transient', '=', False)])]
        views = self._get_and_fix_name_and_find_model_of_all_sql_views()
        for m in models:
            name = '#%s company-manager' % m.model
            access = Access.search([('name','=',name)])
            if m.model in SYSTEM_MODELS:
                rule = Rule.search([('name','=',name)])
                rule.unlink()
                access.unlink()
                continue

            # IR.RULE
            values = {
                'name': name,
                'model_id': m.id,
                'groups': [(4, company_manager_group.id)],
                'domain_force': "[(1, '=', 1)]",
                'perm_read': True,
                'perm_write': True,
                'perm_create': True,
                'perm_unlink': True,
            }
            self._set_rule_values(values)

            # IR.MODEL.ACCESS
            edit = False if m.model.replace('.', '_') in views else True
            values = {
                'name': name,
                'model_id': m.id,
                'group_id': company_manager_group.id,
                'perm_read': True,
                'perm_write': edit,
                'perm_create': edit,
                'perm_unlink': edit,
            }
            if len(access) > 1:
                raise UserError("There are %s manager records with name '%s'! \nCancelling the update of company manager access..." % (str(len(access)), name))
            elif len(access) == 1:
                if not (access.name == name and access.model_id == m and access.group_id == company_manager_group and access.perm_read == True and access.perm_write == edit and access.perm_create == edit and access.perm_unlink == edit):
                    access.write(values)
            else:
                access = Access.create(values)

    def _get_security_rules(self, models=None):
        # return list of dict (name, model, domain, read, write, create, unlink)
        model_type = self._get_model_security_type(models)
        domain = self._get_security_domains()
        rule = []

        for model, type in model_type.items():
            # The name must begin with the hashtag. This is evidence that the rule is created by this script. Other global rules with 'company_id' will be deleted.
            name = '#%%s %s' % model
            comp = 'company'

            if model in ('ir.rule'):
                pass

            elif model == 'res.company':
                company_domain = domain['company'].replace("'company_id'", "'id'")
                rule.append({'name': name%type, 'type': type, 'model': model, 'domain': company_domain, 'read': True, 'write': True, 'create': True, 'unlink': True})

            elif type == 'system':
                # read
                rule.append({'name': name%type, 'type': type, 'model': model, 'domain': domain['system_company'], 'read': True,  'write': False, 'create': False, 'unlink': False})
                # no edit
                rule.append({'name': name%type, 'type': type, 'model': model, 'domain': domain['system'], 'read': False, 'write': True, 'create': True, 'unlink': True})

            elif type == 'company':
                rule.append({'name': name%type, 'type': type, 'model': model, 'domain': domain['company'], 'read': True, 'write': True, 'create': True, 'unlink': True})

            else:
                # read
                rule.append({'name': name%type, 'type': type, 'model': model, 'domain': domain[type], 'read': True,  'write': False, 'create': False, 'unlink': False})
                # edit
                rule.append({'name': name%comp, 'type': comp, 'model': model, 'domain': domain[comp], 'read': False, 'write': True,  'create': True,  'unlink': True})

        return sorted(rule, key = lambda k:k['model'])

    def _get_model_security_type(self, models=None, *args, **kwargs):

        views = self._get_and_fix_name_and_find_model_of_all_sql_views()
        if not models:
            models = [m.model for m in self.env['ir.model'].search([('transient','=',False)])]
        models_published = [f.model for f in self.env['ir.model.fields'].search([('name','=','website_published')])]

        type = {}
        for name in models:

            if name == 'res.users':
                type[name] = 'users'
            elif name in PUBLIC_MODELS:
                type[name] = 'public'
            elif name in SYSTEM_MODELS:
                type[name] = 'system'
            elif name in MODELS_READ_SYSTEM_RECORDS:
                type[name] = 'system_company'
            elif self.env[name]._auto:
                type[name] = 'company'
            elif name.replace('.','_') in views:
                type[name] = 'company'
                # TODO: company manager should read only. New type?
            else:
                pass

            if type.get(name) in ('company','system_company') and name in models_published:
                type[name] += '_published'

        for my_model, my_type in type.items():
            if my_type not in SECURITY_TYPES:
                raise UserError("""'%s' is not a valid security type for model %s. \n
                                    Valid types : %s \n
                                    Cancelling _get_model_security_type""" % (my_type, my_model, str(SECURITY_TYPES)))
        return type

    def _get_security_domains(self):

        # system (no access)
        # users                                                           (company_ids*)
        # public                                                          (company_ids)
        # company                         (child/parent of company_id AND (company_ids))
        # system_company             1 OR (child/parent of company_id AND (company_ids))
        # company_published               (child/parent of company_id AND (company_ids OR website_published))
        # system_company_published   1 OR (child/parent of company_id AND (company_ids OR website_published))

        rule_system_id = " ('company_id','=',1) "
        rule_company_id = " '|',('company_id','child_of',company_id),('company_id','parent_of',company_id) "
        rule_company_ids = " ('company_id','in',company_ids) "
        user_company_ids = " ('company_ids','in',company_ids) "
        rule_website_published = " ('website_published','=',True) "

        domain = {}
        domain['users'] =                                      "[%s]" %                                           (user_company_ids)
        domain['public'] =                                     "[%s]" %                                           (rule_company_ids)
        domain['company'] =                           "['&', %s, %s]" %                          (rule_company_id, rule_company_ids)
        domain['system'] =                   "['&', %s, '&', %s, %s]" %          (rule_system_id, rule_company_id, rule_company_ids)
        domain['system_company'] =           "['|', %s, '&', %s, %s]" %          (rule_system_id, rule_company_id, rule_company_ids)
        domain['company_published'] =                 "['&', %s, '|', %s, %s]" %                 (rule_company_id, rule_company_ids, rule_website_published)
        domain['system_company_published'] = "['|', %s, '&', %s, '|', %s, %s]" % (rule_system_id, rule_company_id, rule_company_ids, rule_website_published)

        return domain

    # Security risk? YES!, if users can set company-specific rules ...
    def _set_rule_values(self, values):
        Rule = self.env['ir.rule']
        rule = Rule.search([('name','=',values['name'])])
        if len(rule) > 1:
            raise UserError("There are %s manager rules with name '%s'! \nCancelling the update of company manager rules..." % (str(len(rule)), values['name']))
        elif len(rule) == 1:
            v = values
            # TODO: how to evaluate rule.groups?
            # - company_manager_group
            # - no group for company security
            if not (rule.name == v['name'] and rule.model_id.id == v['model_id'] and rule.domain_force == v['domain_force'] and rule.perm_read == v['perm_read'] and rule.perm_write == v['perm_write'] and rule.perm_create == v['perm_create'] and rule.perm_unlink == v['perm_unlink']):
                rule.write(values)
        else:
            rule = self.env['ir.rule'].create(values)
        return rule

    def _get_and_fix_name_and_find_model_of_all_sql_views(self):
        # Get views
        self.env.cr.execute("select table_name from information_schema.views where table_schema = 'public';")
        views = [v[0] for v in self.env.cr.fetchall()]
        # Fix view names
        views_fixed = []
        for view in views:
            if view in IRREGULAR_SQL_VIEW_NAMES:
                views_fixed.append(IRREGULAR_SQL_VIEW_NAMES[view])
            else:
                views_fixed.append(view)
        # Check that all views correspond with a model of the same name
        models = [m.model.replace('.','_') for m in self.env['ir.model'].search([])]
        for view in views_fixed:
            if view not in models:
                raise UserError("There is no model corresponding with view '%s'! \n Cancelling _get_and_fix_name_and_find_model_of_all_sql_views" % (view))

        return views_fixed

    def _set_company_id_to_1_where_null(self):
        _logger.debug('set_company_id_to_1_where_null: start')
        self.env.cr.execute("SELECT t.table_name FROM information_schema.tables t INNER JOIN information_schema.columns c ON t.table_name = c.table_name WHERE t.table_type='BASE TABLE' AND c.column_name='company_id' ORDER BY table_name;")
        tables = self.env.cr.fetchall()
        _logger.debug('set_company_id_to_1_where_null: tables = ' + str(tables))
        for table in tables:
            sql = "UPDATE " + table[0] + " SET company_id = 1 WHERE company_id IS NULL;"
            #_logger.debug('sql = ' + str(sql))
            self.env.cr.execute(sql)

        # TODO: set company_id correctly, not 1 on all records!
        #     records = env['ir.model.data'].search([('company_id', '=', None)])
        #     for record in records:
        #         company = record.reference.company_id
        #         record.write({'company_id': company.id})
        # class Rule(models.Model):
        #     _inherit = 'ir.rule'
        #     def post_init_hook(self):
        #         #env = api.Environment(cr, SUPERUSER_ID, {})
        #         records = self.env['ir.model.data'].search([('company_id', '=', None)])
        #         for record in records:
        #             #model, id = record.reference.split(',')
        #             real_record = self.env[record.model].search([('id', '=', record.res_id)])
        #             if real_record:
        #                 # company = self.env[model].browse(int(id)).company_id
        #                 record.write({'company_id': real_record.company_id.id})
