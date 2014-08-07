# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Pexego (<www.pexego.es>). All Rights Reserved
#    $Santiago Argüeso Armesto$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv, fields

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _get_price_unit_invoice(self, cursor, user, move_line, type):
        if not move_line.sale_line_id and not  move_line.purchase_line_id:
            if not move_line.picking_id.address_id:
                return super(stock_picking, self)._get_price_unit_invoice(cursor, user, move_line, type)
            if type == 'out_invoice':
                pricelist = move_line.picking_id.address_id.partner_id.property_product_pricelist and move_line.picking_id.address_id.partner_id.property_product_pricelist.id or False 
            else:
                pricelist = move_line.picking_id.address_id.partner_id.property_product_pricelist_purchase and move_line.picking_id.address_id.partner_id.property_product_pricelist_purchase.id or False
            price = self.pool.get('product.pricelist').price_get(cursor, user, [pricelist],
                    move_line.product_id.id, move_line.product_qty or 1.0, move_line.picking_id.address_id.partner_id.id, {
                        'uom': move_line.product_uom.id,
                        'date': move_line.date,
                        })[pricelist]   
            uom_id = move_line.product_id.uom_id.id
            uos_id = move_line.product_id.uos_id and move_line.product_id.uos_id.id or False
            coeff = move_line.product_id.uos_coeff
            if uom_id != uos_id  and coeff != 0:
                price_unit = price / coeff
                return price_unit
            return price
        return super(stock_picking, self)._get_price_unit_invoice(cursor, user, move_line, type)

stock_picking()

