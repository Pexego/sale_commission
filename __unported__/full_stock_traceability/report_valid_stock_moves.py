# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

"""View that filter stock_moves by not state = 'cancel' Use this view to show traceability tree"""

from osv import osv, fields
from tools.translate import _

class valid_stock_moves(osv.osv):
    """View that filter stock_moves by not state = 'cancel' Use this view to show traceability tree"""
    _name = "valid.stock.moves"
    _auto = False


    def _get_simplified_trace_up(self, cr, uid, ids, field_name, arg, context):
        """get the last childs moves for a specific move"""
        res = {}
        for move in self.browse(cr, uid, ids):
            cr.execute("select id from stock_move_parents(%s)", (move.id,))
            records = []
            for record in cr.fetchall():
                records.append(record[0])
            if records[0] in ids:
                res[move.id] = []
            else:
                res[move.id] = records
        return res

    def _get_simplified_trace_down(self, cr, uid, ids, field_name, arg, context):
        """get the top parents moves for a specific move"""
        res = {}
        for move in self.browse(cr, uid, ids):
            cr.execute("select id from stock_move_childs(%s)", (move.id,))
            records = []
            for record in cr.fetchall():
                records.append(record[0])
            if records[0] in ids:
                res[move.id] = []
            else:
                res[move.id] = records
        return res

    def _get_move_type(self, cr, uid, ids, field_name, arg, context = {}):
        """get the type of move for do more accessibly traceability tree"""
        return self.pool.get('stock.move').get_move_type(cr, uid, ids, context=context)

    _columns = {
            'id': fields.integer('id', readonly=True),
            'name': fields.char('Name', size=64, readonly=True, select=True),
            'product_id': fields.many2one('product.product', 'Product', readonly=True, select=True),
            'product_qty': fields.float('Quantity', readonly=True),
            'product_uom': fields.many2one('product.uom', 'Product UOM', readonly=True, select=True),
            'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', readonly=True, select=True),
            'expiry_date': fields.datetime('Expiry Date', readonly=True),
            'supplier': fields.char('Supplier', size=64, readonly=True),
            'tracking_id': fields.many2one('stock.tracking', 'Pack', select=True, readonly=True),
            'product_packaging': fields.many2one('product.packaging', 'Packaging', readonly=True, select=True),
            'picking_id': fields.many2one('stock.picking', 'Packing List', readonly=True, select=True),
            'location_id': fields.many2one('stock.location', 'Location', readonly=True, select=True),
            'location_dest_id': fields.many2one('stock.location', 'Dest. Location', readonly=True, select=True),
            'date': fields.datetime('Date Created', readonly=True),
            'date_expected': fields.datetime('Date', readonly=True),
            'state': fields.selection([('draft', 'Draft'), ('waiting', 'Waiting'), ('confirmed', 'Not Available'), ('assigned', 'Available'), ('done', 'Done'), ('cancel', 'Cancelled')],'State', size=12, readonly=True),
            'move_history_simplified_up': fields.function(_get_simplified_trace_up, method=True, relation='stock.move', type="many2many", string='Traceability simplified upstream'),
            'move_history_simplified_down': fields.function(_get_simplified_trace_down, method=True, relation='stock.move', type="many2many", string='Traceability simplified downstream'),
            'move_history_ids': fields.many2many('stock.move', 'stock_move_history_ids', 'parent_id', 'child_id', 'Move History'),
            'move_history_ids2': fields.many2many('stock.move', 'stock_move_history_ids', 'child_id', 'parent_id', 'Move History'),
            'move_type': fields.function(_get_move_type, method=True, string='Type', type="char", size=24, readonly=True),
            'production_id': fields.many2one('mrp.production', 'Production', readonly=True, select=True)
    }

    def init(self, cr):
        """creates view when install"""
        cr.execute("""
            create or replace view valid_stock_moves as (
                select stock_move.id as id,stock_move.name as name,stock_move.product_id as product_id,product_qty,product_uom,prodlot_id,stock_production_lot.life_date as expiry_date,
                    supplier,tracking_id,product_packaging,picking_id,location_id,location_dest_id,stock_move.date as date,
                    date_expected,state,production_id
                from stock_move left join stock_production_lot on stock_move.prodlot_id = stock_production_lot.id
                where state not in ('cancel')
            )""")

    def unlink(self, cr, uid, ids, context={}):
        """not can delete, beacause is database view"""
        raise osv.except_osv(_('Error !'), _('You cannot delete any record!'))


valid_stock_moves()