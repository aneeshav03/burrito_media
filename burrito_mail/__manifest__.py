# -*- coding: utf-8 -*-
{
    "name": "Contacts | Send Contract and Welcome Email",
    "summary": "Contacts | Send Contract and Welcome Email",
    "description": """Contacts | Send Contract and Welcome Email""",
    "author": "Aneesh.AV",
    "auto_install": True,
    "application": True,
    "installable": True,
    "license": "Other proprietary",
    "sequence": 1,
    "version": "16.0.1.0.1",
    "depends": ["sign", "mail", "crm"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "data/email_template.xml",
        "data/agreement_attachment.xml",
        "wizard/agreement_sign_views.xml",
        "views/res_config_view.xml",
        "views/res_partner_view.xml",
    ],
}
