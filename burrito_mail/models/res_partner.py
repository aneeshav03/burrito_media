# -*- coding: utf-8 -*-
from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    sign_request_ids = fields.One2many(
        "sign.request", "partner_id", string="Signature Requests"
    )
    sign_request_count = fields.Integer(
        "# of Signature Requests", compute="_compute_sign_request_count"
    )

    def _compute_sign_request_count(self):
        """
        This function is used to compute the count of sign requests for each partner.

        Parameters:
        self: The object instance.

        Returns:None
        """
        sign_data = self.env["sign.request"].read_group(
            domain=[("partner_id", "in", self.ids)],
            fields=["partner_id"],
            groupby=["partner_id"],
        )

        mapped_data = dict(
            [(m["partner_id"][0], m["partner_id_count"]) for m in sign_data]
        )
        for partner in self:
            partner.sign_request_count = mapped_data.get(partner.id, 0)

    def action_view_sign(self):
        """This method defines the action to view
        the sign request associated with the partner.
        """
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("sign.sign_request_action")
        if len(self.sign_request_ids) > 1:
            action["domain"] = [("partner_id", "=", self.id)]
        elif len(self.sign_request_ids) == 1:
            action["views"] = [(False, "form")]
            action["res_id"] = self.sign_request_ids.ids[0]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    def send_welcome_mail(self, partner):
        """
        This function is used to send a welcome email to a new partner.

        Parameters:
        self: The object instance.
        partner: The partner to whom the welcome email is to be sent.

        Returns:None
        """
        email_template = self.env.ref("burrito_mail.welcome_email_template", False)
        partner.message_post_with_template(
            email_template.id,
            composition_mode="mass_mail",
            message_type="comment",
            model="res.partner",
            res_id=partner.id,
        )
