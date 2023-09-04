# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    geo_targeting = fields.Text()
    tactic = fields.Text()
    audience = fields.Text()
    estimated_reach = fields.Float(compute="_compute_estimated_values", store=False)
    estimated_impressions = fields.Float(
        compute="_compute_estimated_values", store=False
    )
    cpm = fields.Float(related="product_id.lst_price", readonly=False, store=True)

    @api.depends("price_unit", "price_subtotal", "cpm")
    def _compute_estimated_values(self):
        """
        This method computes the estimated_impressions and the estimated_reach
        """
        for line in self:
            line.estimated_impressions = 0
            line.estimated_reach = 0
            if line.cpm > 0:
                line.estimated_impressions = (line.price_subtotal / line.cpm) * 1000
                line.estimated_reach = line.estimated_impressions / 3 / 4
