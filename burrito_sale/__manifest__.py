# -*- coding: utf-8 -*-
{
    "name": "Burrito | Sale Extension",
    "summary": "Burrito | Sale Extension",
    "description": """Burrito | Sale Extension""",
    "author": "Aneesh.AV",
    "auto_install": True,
    "application": True,
    "installable": True,
    "license": "Other proprietary",
    "sequence": 1,
    "version": "16.0.1.0.1",
    "depends": ["sale_management"],
    # always loaded
    "data": [
        "views/sale_portal_template.xml",
        "views/sale_report_template.xml",
        "views/sale_order_view.xml",
    ],
}
