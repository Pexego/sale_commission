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

"""inherits stock.production lot, adds methods that get production lots hierarchical or manages production lot sequence"""

from osv import fields, osv
import decimal_precision as dp

class stock_production_lot(osv.osv):
    """inherits stock.production lot, adds unit price"""
    _inherit = 'stock.production.lot'

    _columns = {
                'unit_price': fields.float('Cost Price', required=True, digits_compute=dp.get_precision('Product UoM')),
            }

    _defaults = {
        'unit_price': lambda *a: 0.00
    }

    def on_change_product_id(self, cr, uid, ids, product):
        """on change product id in production lot form fills unit_price and product_uom"""
        if not product:
            return {}
        product_obj_id = self.pool.get('product.product').browse(cr, uid, product)
        result = {'unit_price': product_obj_id.product_tmpl_id.standard_price}
        return {'value': result}

stock_production_lot()