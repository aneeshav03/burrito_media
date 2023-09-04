# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
