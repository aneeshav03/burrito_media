# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # add the custom field for default template
    agreement_sign_tmpl_id = fields.Many2one(
        "sign.template",
        related="company_id.agreement_sign_tmpl_id",
        string="Default Document",
        readonly=False,
    )
