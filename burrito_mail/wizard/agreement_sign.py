# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, Command


class AgreementSign(models.TransientModel):
    _name = "agreement.sign.wizard"
    _description = "Sign document in Agreement"

    def _get_sign_template_ids(self):
        return self.env.company.agreement_sign_tmpl_id.ids

    def _get_sign_role_id(self):
        return self.env["sign.item.role"].browse(1).id

    partner_id = fields.Many2one(
        "res.partner",
        string="Partners",
        default=lambda s: s.env.context.get("active_id", None),
        readonly=False,
    )

    responsible_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user.id
    )
    partner_role_id = fields.Many2one(
        "sign.item.role",
        string="Partner Role",
        required=True,
        domain="[('id', 'in', sign_template_responsible_ids)]",
        default=_get_sign_role_id,
        store=True,
        readonly=False,
    )
    sign_template_responsible_ids = fields.Many2many(
        "sign.item.role", compute="_compute_responsible_ids"
    )
    possible_template_ids = fields.Many2many(
        "sign.template", compute="_compute_possible_template_ids"
    )
    sign_template_ids = fields.Many2many(
        "sign.template",
        string="Documents to sign",
        domain="[('id', 'in', possible_template_ids)]",
        default=_get_sign_template_ids,
        required=True,
    )
    subject = fields.Char(required=True, default="Signature Request")
    message = fields.Html()
    cc_partner_ids = fields.Many2many("res.partner", string="Copy to")
    attachment_ids = fields.Many2many("ir.attachment")

    @api.depends("sign_template_responsible_ids")
    def _compute_partner_role_id(self):
        for wizard in self:
            if wizard.partner_role_id not in wizard.sign_template_responsible_ids:
                wizard.partner_role_id = False
            if len(wizard.sign_template_responsible_ids) == 1:
                wizard.partner_role_id = wizard.sign_template_responsible_ids._origin

    @api.depends("sign_template_ids.sign_item_ids.responsible_id")
    def _compute_responsible_ids(self):
        for wizard in self:
            responsible_ids = self.env["sign.item.role"]
            for sign_template_id in wizard.sign_template_ids:
                if responsible_ids:
                    responsible_ids &= sign_template_id.sign_item_ids.responsible_id
                else:
                    responsible_ids |= sign_template_id.sign_item_ids.responsible_id
            wizard.sign_template_responsible_ids = responsible_ids

    @api.depends("sign_template_ids")
    def _compute_possible_template_ids(self):
        possible_sign_templates = self._get_sign_template_ids()
        self.possible_template_ids = possible_sign_templates

    def validate_signature(self):
        """This function validates and send the signature request of a partner.
        It first checks if the partner has a work email set. If not,
        it displays a notification message.

        Then it creates a sign request for the partner.

        The function then creates a list of sign values for each sign template
        associated with the partner.

        After creating the sign values,the function creates
        a sign request for each sign value.

        The function then subscribes the partner to the sign requests.
        If the partner does not have write access rights,
        the function uses sudo to bypass the access rights.

        Finally, if the partner is the only one who has to sign,
        the function posts a message notifying the partner
        of the new signature request. If the responsible person is also a signatory,
        the function posts a message notifying both the partner and the responsible
        person of the new signature request.

        If there is only one sign request and the user is the responsible person,
        the function redirects the user to the document to be signed.
        Otherwise, it returns True.

        Args: self: The instance of the class.

        Returns: True or a redirection to the document to be signed.
        """
        self.ensure_one()
        if not self.partner_id.email:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "message": _(
                        "%s does not have a work email set.", self.partner_id.name
                    ),
                    "sticky": False,
                    "type": "danger",
                },
            }

        sign_request = self.env["sign.request"]
        if not self.check_access_rights("create", raise_exception=False):
            sign_request = sign_request.sudo()

        sign_values = []
        sign_templates_employee_ids = self.sign_template_ids.filtered(
            lambda t: len(t.sign_item_ids.mapped("responsible_id")) == 1
        )
        sign_templates_both_ids = self.sign_template_ids - sign_templates_employee_ids
        for sign_template_id in sign_templates_employee_ids:
            sign_values.append(
                (
                    sign_template_id,
                    self.partner_id,
                    [
                        {
                            "role_id": self.partner_role_id.id,
                            "partner_id": self.partner_id.id,
                            "mail_send_order": 2,
                        }
                    ],
                )
            )
        for sign_template_id in sign_templates_both_ids:
            second_role = (
                sign_template_id.sign_item_ids.responsible_id - self.partner_role_id
            )
            sign_values.append(
                (
                    sign_template_id,
                    self.partner_id,
                    [
                        {
                            "role_id": self.partner_role_id.id,
                            "partner_id": self.partner_id.id,
                            "mail_sent_order": 2,  # assign the sign order
                        },
                        {
                            "role_id": second_role.id,
                            "partner_id": self.responsible_id.partner_id.id,
                            "mail_sent_order": 1,  # assign the sign order
                        },
                    ],
                )
            )
        sign_requests = self.env["sign.request"].create(
            [
                {
                    "template_id": sign_request_values[0].id,
                    "partner_id": self.partner_id.id,  # add customer to the request
                    "request_item_ids": [
                        Command.create(
                            {
                                "partner_id": signer["partner_id"],
                                "role_id": signer["role_id"],
                                "mail_sent_order": signer["mail_sent_order"],
                            }
                        )
                        for signer in sign_request_values[2]
                    ],
                    "reference": _(
                        "Signature Request - %s", sign_request_values[0].name
                    ),
                    "subject": self.subject,
                    "message": self.message,
                    "attachment_ids": [
                        (4, attachment.copy().id) for attachment in self.attachment_ids
                    ],  # Attachments may not be bound to multiple sign requests
                }
                for sign_request_values in sign_values
            ]
        )
        sign_requests.message_subscribe(partner_ids=self.cc_partner_ids.ids)

        if not self.check_access_rights("write", raise_exception=False):
            sign_requests = sign_requests.sudo()

        if self.partner_id:
            if self.responsible_id and sign_templates_both_ids:
                signatories_text = _(
                    "%s and %s are the signatories.",
                    self.partner_id.name,
                    self.responsible_id.display_name,
                )
            else:
                signatories_text = _("Only %s has to sign.", self.partner_id.name)
            record_to_post = self.partner_id

            record_to_post.message_post(
                body=_(
                    "%s requested a new signature on the"
                    "following documents:<br/><ul>%s</ul>%s"
                )
                % (
                    self.env.user.display_name,
                    "\n".join(
                        "<li>%s</li>" % name
                        for name in self.sign_template_ids.mapped("name")
                    ),
                    signatories_text,
                )
            )

        if len(sign_requests) == 1 and self.env.user.id == self.responsible_id.id:
            return sign_requests.go_to_document()
        return True
