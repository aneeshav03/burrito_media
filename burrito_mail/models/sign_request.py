from odoo import fields, models


import logging

_logger = logging.getLogger(__name__)


class SignRequest(models.Model):
    _inherit = "sign.request"

    partner_id = fields.Many2one("res.partner", string="Partner")

    def _sign(self):
        """
        This function will overwrite the existing
        Check the both parties signed the request, then send welcome email
        Also attachment will created to the customer record
        """
        res = super(SignRequest, self)._sign()
        for request in self:
            if request.partner_id:
                if self.state == "signed":
                    request.partner_id.send_welcome_mail(request.partner_id)
                self.env["ir.attachment"].create(
                    {
                        "name": request.reference,
                        "datas": request.completed_document,
                        "type": "binary",
                        "res_model": self.env["res.partner"]._name,
                        "res_id": request.partner_id.id,
                    }
                )
        return res
