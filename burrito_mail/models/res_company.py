from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    # add the custom field for default template
    agreement_sign_tmpl_id = fields.Many2one(
        "sign.template",
        string="Default Document Template for Agreement",
    )
