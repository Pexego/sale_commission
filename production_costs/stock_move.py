# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Pexego (<www.pexego.es>). All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""stock_move inherit, manage stock moves for check traceability and mixes"""

from osv import osv, fields
import decimal_precision as dp

class stock_move(osv.osv):
    """stock_move inherit for manage total prices"""
    _inherit = 'stock.move'

    def _get_total_price(self, cr, uid, ids, field_name, arg, context = {}):
        """obtains price of prodlots unit price with quantity"""
        res = {}
        for move in self.browse(cr, uid, ids):
            res[move.id] = None
            if move.prodlot_id and move.prodlot_id.unit_price:
                if move.product_id.uom_id.id != move.product_uom.id:
                    res[move.id] = move.prodlot_id.unit_price * self.pool.get('product.uom')._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id)
                else:
                    res[move.id] = move.prodlot_id.unit_price * move.product_qty
        return res

    _columns = {
            'price': fields.function(_get_total_price, method=True, string="Cost Price", type='float', readonly=True, digits_compute=dp.get_precision('Product UoM')),
        }

stock_move()