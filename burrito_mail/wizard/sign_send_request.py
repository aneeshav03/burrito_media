from odoo import fields, models


class SignSendRequest(models.TransientModel):
    _inherit = "sign.send.request"

    partner_id = fields.Many2one("res.partner", string="Partner")

    def create_request(self):
        sign_request = super(SignSendRequest, self).create_request()
        if self.partner_id:
            sign_request.partner_id = self.partner_id
        return sign_request
