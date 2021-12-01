# Multi-company instead of multi-database

This module implements security and configurations between companies in a database.

## Why?

With very small, very similar companies, it might be easier to manage them in one database.

## Security

- A user cannot access any data which is not belonging to the active company or its parent/child companies.

- A company manager can access all data in the active company and its parent/child companies.

## Configurations

When you create a new company or install/update/uninstall a module,
some company configurations are set by Administrator (user id 2).
E.g. create a mail channel for all employees of the company.

## How to install?

Apply patches:
- git apply /path/to/multicompany_instead_of_multidatabase/patches/*
- git commit

For new database: Restart Odoo, create a new database, install the module
- python odoo-bin -i multicompany_instead_of_multidatabase -d MYDATABASE

For existing database:
- Run SQL: "UPDATE ir_module_module SET state = 'to install' WHERE name = 'base';"
    (state must be 'to install', not 'uninstalled')
- python odoo-bin -i base,multicompany_instead_of_multidatabase -d MYDATABASE

## How to use?

Create a new company (ignore the security error).
Go to a list view, e.g. Companies or Users (to avoid another security error).
Select the new company in the top right dropdown menu.
Go to Users.
Do for each user:
- Edit
- A) Write a name and select a language (will create a new partner)
- B) Select an existing partner
- Save

Company with id 1 is considered the SYSTEM company

## Security vulnerabilities

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

## Bugs

Error in log just after creating a new company.
Add company id to URL cids to avoid access error.
(This doesn't work: self.env.companies = new_company # The new environment "stops" in the api.py call_kw_model_create.)

res.users temp_partner_id should be deleted. I see no method in openupgradelib to completely delete a field! (Just the db column...)

## Roadmap

Improve company_id for external IDs.
Import company from another database.
Export company to another database.

## How to contribute?

You are very welcome to help with the tasks in the roadmap!
Please sign the OCA document (I would like to move the repo to OCA).

## Author

AppsToGrow
Contact: Henrik Norlin
Email: henrik@appstogrow.co
Mobile: +4791120745

## Supported versions

- 14.0
