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

"""inherits from stock.production.lot adds functionally for blocked prodlots"""

from osv import osv, fields
import time

class stock_production_lot(osv.osv):
    """inherits from stock.production.lot adds functionally for blocked prodlots"""
    _inherit = 'stock.production.lot'
   
    def _get_blocked_prodlots_up(self, cr, uid, ids, field_name, arg, context=None):
        """get blocked or to block prodlots upstream by specific prodlot"""
        if context is None: context = {}
        res = {}
        for obj_prodlot_id in self.browse(cr, uid, ids):
            cr.execute("select id from block_prodlots_up(%s)", (obj_prodlot_id.id,))
            records = []
            if cr.rowcount:
                for record in cr.fetchall():
                    records.append(record[0])
                if records[0] in ids:
                    res[obj_prodlot_id.id] = []
                else:
                    res[obj_prodlot_id.id] = records
            else:
                res[obj_prodlot_id.id] = []
        return res

    def _get_blocked_prodlots_down(self, cr, uid, ids, field_name, arg, context=None):
        """get blocked or to block prodlots downstream by specific prodlot"""
        if context is None: context = {}
        res = {}
        for obj_prodlot_id in self.browse(cr, uid, ids):
            cr.execute("select id from block_prodlots_down(%s)", (obj_prodlot_id.id,))
            records = []
            if cr.rowcount:
                for record in cr.fetchall():
                    records.append(record[0])
                if records[0] in ids:
                    res[obj_prodlot_id.id] = []
                else:
                    res[obj_prodlot_id.id] = records
            else:
                res[obj_prodlot_id.id] = []
        return res

    def _get_if_in_alert(self, cr, uid, ids, field_name, arg, context=None):
        """get if prodlots is in alert beacause was included in blocked case"""
        if context is None: context = {}
        res = {}
        for obj_prodlot_id in self.browse(cr, uid, ids):
            if obj_prodlot_id.blocked_prodlots_cases_ids:
                value = True
                for blocked_prodlot_case_id in obj_prodlot_id.blocked_prodlots_cases_ids:
                    if blocked_prodlot_case_id.state in ['confirm','cancelled']:
                        value = False
                        break

                res[obj_prodlot_id.id] = value
            else:
                res[obj_prodlot_id.id] = False
        return res

    def _get_if_blocked(self, cr, uid, ids, field_name, arg, context=None):
        """get if prodlots is blocked beacause was included in confirm blocked case"""
        if context is None: context = {}
        res = {}
        for obj_prodlot_id in self.browse(cr, uid, ids):
            if obj_prodlot_id.blocked_prodlots_cases_ids:
                value = False
                for blocked_prodlot_case_id in obj_prodlot_id.blocked_prodlots_cases_ids:
                    if blocked_prodlot_case_id.state == 'confirm':
                        value = True
                        break

                res[obj_prodlot_id.id] = value
            else:
                res[obj_prodlot_id.id] = False
        return res

    def _get_prodlots_to_update_from_block_cases(self, cr, uid, ids, context=None):
        """return prodlots lines to updats it raises from block cases when update"""
        if context is None: context = {}
        result = []
        for block_case_id in self.browse(cr, uid, ids):
            for prodlot_obj_id in block_case_id.blocked_prodlots_ids:
                result.append(prodlot_obj_id.id)
        return result

    _columns = {
        'in_alert': fields.function(_get_if_in_alert, method=True, type="boolean", string="In Alert",
            store={'block.prodlot.cases': (_get_prodlots_to_update_from_block_cases, ['state'], 10),
                        'stock.production.lot': (lambda self, cr, uid, ids, c={}: ids, None, 20)}),
        'blocked': fields.function(_get_if_blocked, method=True, type="boolean", string='Blocked',
            store={'block.prodlot.cases': (_get_prodlots_to_update_from_block_cases, ['state'], 10),
                        'stock.production.lot': (lambda self, cr, uid, ids, c={}: ids, None, 20)}),
        'blocked_prodlots_up': fields.function(_get_blocked_prodlots_up, method=True, relation='stock.production.lot', type="many2many", string='Block poduction lots upstream'),
        'blocked_prodlots_down': fields.function(_get_blocked_prodlots_down, method=True, relation='stock.production.lot', type="many2many", string='Block poduction lots downstream')
    }

    # pylint: disable-msg=W0141
    def search_affected_prodlots(self, cr, uid, ids, optimistic = False):
        """set in_alert to all prodlots affected upstream and downstream for specific prodlot"""
        obj_prodlot_id = self.browse(cr, uid, ids)
        prodlots_to_warn = []
        
        if not optimistic:
            prodlots_to_warn = list(set(obj_prodlot_id.blocked_prodlots_up + obj_prodlot_id.blocked_prodlots_down))
        else:
            prodlots_to_warn = obj_prodlot_id.blocked_prodlots_up

        return [x.id for x in prodlots_to_warn]


    def block_production_lot(self, cr, uid, prodlot_id, context = {}):
        """contents the functionallity of block a specific production lot"""
        obj_prodlot_id = self.browse(cr, uid, prodlot_id)

        prodlots_ids = self.pool.get('stock.report.prodlots').search(cr, uid, [('prodlot_id', '=', obj_prodlot_id.id), ('qty', '>', 0)])
        if prodlots_ids:
            obj_pool_move = self.pool.get('stock.move')
            #goes around the found locations
            for prodlot in prodlots_ids:
                if self.pool.get('stock.location').browse(cr, uid, prodlot.location_id.id).usage in ('internal'):
                    #gets the last move for this product_lot in the location
                    move = obj_pool_move.get_last_destination_move(cr, uid, prodlot.location_id.id, obj_prodlot_id.id)
                    if move:
                        move_obj = obj_pool_move.browse(cr, uid, move)
                        #creates a stock_move, because moves the prodlot blocked to waste
                        obj_pool_move.create(cr, uid, vals = {
                             'product_uom' :move_obj.product_uom.id,
                             'product_uos_qty' : move_obj.product_uos_qty,
                             'date' : time.strftime('%Y-%m-%d %H:%M:%S'),
                             'product_qty' : prodlot.qty,
                             'product_uos' : move_obj.product_uos,
                             'location_id' : prodlot.location_id.id,
                             'product_id' : move_obj.product_id.id,
                             'name' : 'M:' + str(obj_prodlot_id.product_id.product_tmpl_id.property_waste.id) + 'TOWST' + time.strftime('%Y-%m-%d %H:%M:%S'),
                             'date_expected' : time.strftime('%Y-%m-%d %H:%M:%S'),
                             'state' : 'done',
                             'location_dest_id' : obj_prodlot_id.product_id.product_tmpl_id.property_waste.id,
                             'prodlot_id': obj_prodlot_id.id,
                            })

stock_production_lot()