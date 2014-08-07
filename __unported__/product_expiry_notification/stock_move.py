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
"""inherits fromk stock_move for checks expired prodlots"""

from osv import osv
from tools.translate import _

class stock_move(osv.osv):
    """inherits fromk stock_move for checks expired prodlots"""
    _inherit = "stock.move"

    def _check_prodlot_expiration(self, cr, uid, ids):
        """checks if prodlot is expired and is trying move it to internal or customer location"""
        for move in self.browse(cr, uid, ids):
            if move.prodlot_id and move.location_dest_id:
                if move.prodlot_id.expired and move.location_dest_id.usage in ['internal', 'customer']:
                    return False
        return True

    _constraints = [
    (_check_prodlot_expiration, _('Cannot move an expired production lot to internal or customer location'), ['expired']),
    ]

    def eval_onchange_lot_date(self, cr, uid, res, prodlot_id = False):
        """overwrites this event for shows a warning if the production lot selected is expired"""
        prodlot = prodlot_id or ((res.get('value') and res['value'].get('prodlot_id')) and res['value']['prodlot_id'] or False)
        if res.get('warning', False):
            return res
        elif prodlot:
            obj_prodlot_id = self.pool.get('stock.production.lot').browse(cr, uid, prodlot)
            if obj_prodlot_id.expired:
                res['warning'] = {
                    'title': _('Production Lot Expired!'),
                    'message': _('This production lot is expired'),
                        }
                return {'warning': res['warning'], 'value': res.get('value') and res['value'].update({'prodlot_id': None}) or {'prodlot_id': None}}
        return res

    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False, loc_id=False, product_id=False, uom_id=False, context=None):
        """overwrites this event for shows a warning if the production lot selected is on alert"""
        if context is None: context = {}
        if not prodlot_id or not loc_id:
            return {}

        res = super(stock_move, self).onchange_lot_id(cr, uid, ids, prodlot_id = prodlot_id, product_qty = product_qty, loc_id = loc_id, product_id=product_id, uom_id=uom_id, context = context)
        return self.eval_onchange_lot_date(cr, uid, res, prodlot_id)

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, address_id=False, prod_qty=0.0, prodlot_id=False):
        """Extends this event checking prodlot obtained"""
        res = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, address_id)

        return self.eval_onchange_lot_date(cr, uid, res)

    def onchange_location_id(self, cr, uid, ids, product_id = False, location_id = False, dummy = False, product_qty=False, product_uom_id=False):
        """event fires when changes the location, checks the location and return a default production lot for this location"""
        res = super(stock_move, self).onchange_location_id(cr, uid, ids,product_id,location_id,dummy,product_qty,product_uom_id)

        return self.eval_onchange_lot_date(cr, uid, res)

stock_move()
