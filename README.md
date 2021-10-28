# Strict security between companies

These modules implement strict security between companies in a database.

A user cannot access any data which is not belonging to the active company or its parent/child companies.

A company manager can access all data in the active company and its parent/child companies.

## Why?

With very small, very similar companies, it might be easier to manage them in one database.

## How to install?

Apply patch:
- base_company_security/users-company_dependent-partner.patch

Install base_company_security

## How to use?

Create a new company.
Go to Companies.
Select the new company.

Users with access to multiple companies should for each company select or create a partner.

## Roadmap

Users form: Button to create a partner (if missing).

Implement users company_dependent partner for more modules.

Block the database cursor in safe_eval.

Improve company_id for external IDs.

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
