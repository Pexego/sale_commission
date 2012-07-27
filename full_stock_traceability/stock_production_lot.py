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
from tools.translate import _
import time

def sort_by_qty( item_x, item_y ):
    """compare parent_location elements by qty"""
    if item_x[2] < item_y[2]:
        rst = -1
    elif item_x[2] > item_y[2]:
        rst = 1
    else :
        rst = 0
    return rst

class stock_production_lot(osv.osv):
    """inherits stock.production lot, adds methods that get production lots hierarchical or manages production lot sequence"""
    _inherit = 'stock.production.lot'
    _order = "date desc"

    def _get_supplier(self, cr, uid, ids, field_name, arg, context=None):
        """gets the name of the supplier"""
        if context == None: context = {}
        res = {}
        for prodlot_id in ids:
            res[prodlot_id] = None
            move_ids = self.pool.get('stock.move').search(cr, uid, [('prodlot_id', '=', prodlot_id)])
            for move_id in move_ids:
                move = self.pool.get('stock.move').browse(cr, uid, move_id)
                if move.location_id.name == 'Suppliers':
                    if move.picking_id:
                        res[prodlot_id] = move.picking_id.address_id.partner_id.name
                        break
        return res

    def _get_parent_moves(self, cr, uid, ids, field_name, arg, context=None):
        """gets the name of the supplier"""
        if context == None: context = {}
        res = {}
        for prodlot_id in ids:

            move_ids = self.pool.get('valid.stock.moves').search(cr, uid, [('prodlot_id', '=',prodlot_id)])
            if move_ids:
                cr.execute("""select stock_move.id from stock_move inner join stock_production_lot
                on stock_move.prodlot_id = stock_production_lot.id where stock_move.id in %s and
                (stock_move.id not in (select child_id from stock_move_history_ids) or
                (is_mix = True and prodlot_id not in (select distinct prodlot_id from stock_move AS sm
                inner join stock_move_history_ids on sm.id = parent_id
                where child_id in (stock_move.id))) or production_id is not null)""", (tuple(move_ids),))

                ids = []
                for (parent_id,) in cr.fetchall():
                    ids.append(parent_id)

                res[prodlot_id] = ids
            else:
                res[prodlot_id] = []
        return res

    _columns = {
                'is_mix': fields.boolean('Mix'),
                'supplier': fields.function(_get_supplier, method=True, string="Supplier", type='char'),
                'parent_move_ids': fields.function(_get_parent_moves, method=True, string="Parent moves", type="one2many", readonly=True, relation="valid.stock.moves")
            }
    _defaults = {
            'is_mix': lambda *a: 0,
        }

    def get_all_parent_location(self, cr, uid, obj_location, product_id, qty, deep=False):
        """searches all the prodlots, quantities and locations for a location and his child locations"""
        locations_list = []
        if deep:
            locations = self.pool.get('stock.location').search(cr, uid, [('location_id', 'child_of', [obj_location.id])])
        else:
            locations = [obj_location.id]
            
        product_obj = self.pool.get('product.product').browse(cr, uid, product_id)
        #gets the prodlot, the quantity of this prodlot and the location where is the prodlot by location, product and quantity
        for location in locations:
            lots = self.pool.get('stock.location').get_lots_inside(cr, uid, location, product_id)

            total_lot_stock = sum([(product_obj.uom_id.uom_type == 'bigger' and  lot.stock_available / product_obj.uom_id.factor or lot.stock_available * product_obj.uom_id.factor) for lot in self.pool.get('stock.production.lot').browse(cr, uid, lots, context={'location_id': location})])
            if total_lot_stock >= qty:
                for lot in self.pool.get('stock.production.lot').browse(cr, uid, lots, context={'location_id': location}):
                    locations_list.append((lot.id, location,  (product_obj.uom_id.uom_type == 'bigger' and  lot.stock_available / product_obj.uom_id.factor or lot.stock_available * product_obj.uom_id.factor)))

        locations_list.sort(sort_by_qty)

        return locations_list
    
    def get_default_production_lot(self, cr, uid, location, product_id, qty_needed, deep=False, notvalidprodlots = []):
        """gets a prodution lot for a product in location, gets the production lot with less usability time and with less quatity"""
        #gets all prodlots in the location with this product and stock are enough
        split = False
        obj_location_id = self.pool.get('stock.location').browse(cr, uid, location)
        default_prodlot = False
        prodlot_location = False
        default_qty = False
        res = self.get_all_parent_location(cr, uid, obj_location_id, product_id, qty_needed, deep)

        #by default the first registry
        if res:
            #checks if the prodlots not are used, if used remove it
            if notvalidprodlots:
                recordstoremove = []
                for record in res:
                    for prodlot in notvalidprodlots:
                        if record == prodlot:
                            recordstoremove.append(record)
                            break
                for toremove in recordstoremove:
                    res.remove(toremove)

            if res:
                firstobj_production_lot = self.browse(cr, uid, res[0][0])
                prodlot_location = res[0][1]
                default_qty = res[0][2]

                #checks if advice to split
                if default_qty < qty_needed:
                    split = True

                expirydate = firstobj_production_lot.life_date
                default_prodlot = firstobj_production_lot.id

                for record in res:
                    if record[2] < qty_needed:
                        continue

                    obj_prodlot = self.browse(cr, uid, record[0])
                    if default_qty < qty_needed:
                        firstobj_production_lot = self.browse(cr, uid, record[0])
                        default_prodlot = firstobj_production_lot.id
                        expirydate = firstobj_production_lot.life_date
                        prodlot_location = record[1]
                        default_qty = record[2]

                    if obj_prodlot.life_date:
                        if expirydate:
                            #if life_date of this product is less that life_date for default, changes the default values
                            if time.strptime(expirydate, '%Y-%m-%d %H:%M:%S') > time.strptime(obj_prodlot.life_date, '%Y-%m-%d %H:%M:%S'):
                                expirydate = obj_prodlot.life_date
                                default_qty = record[2]
                                default_prodlot = obj_prodlot.id
                                prodlot_location = record[1]
                        else:
                            #if the first prodlot not have expirydate, changes the default values
                            expirydate = obj_prodlot.life_date
                            default_prodlot = obj_prodlot.id
                            prodlot_location = record[1]
                            default_qty = record[2]
                            
                    if record[2] < default_qty:
                        default_qty = record[2]
                        expirydate = obj_prodlot.life_date
                        default_prodlot = obj_prodlot.id
                        prodlot_location = record[1]

        if default_qty < qty_needed:
            default_qty = 0.0
            default_prodlot = False
            prodlot_location = False
        
        if deep:
            return default_prodlot, prodlot_location, default_qty, split
        else:
            return default_prodlot, split

    def unlink(self, cr, uid, ids, context = {}):
        """Overwrites unlink method to avoid delete lots with moves"""
        for prodlot_id in self.browse(cr, uid, ids):
            move_ids = self.pool.get('stock.move').search(cr, uid, [('prodlot_id', '=', prodlot_id.id)])
            if move_ids:
                raise osv.except_osv(_('Error !'), _('You cannot delete this lot because it has moves depends on!'))

        return super(stock_production_lot, self).unlink(cr, uid, ids, context = context)

    def action_simplified_traceability(self, cr, uid, ids, context=None):
        """calls to simplified traceability wizard"""
        if context is None: context = {}

        value=self.pool.get('action.simplified.traceability').action_traceability(cr,uid,ids,context)
        return value
    
stock_production_lot()