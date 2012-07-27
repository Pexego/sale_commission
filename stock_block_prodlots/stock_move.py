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

"""inherits fromk stock_move for checks blocked prodlots"""

from osv import osv, fields
from tools.translate import _

class stock_move(osv.osv):
    """inherits fromk stock_move for checks blocked prodlots"""
    _inherit = "stock.move"

    def get_move_type(self, cr, uid, ids, context=None):
        """add new move types"""
        if context is None: context = {}

        res = super(stock_move, self).get_move_type(cr, uid, ids, context=context)

        for move in self.browse(cr, uid, ids, context=context):
            if move.location_dest_id.usage == 'elimination':
                res[move.id] = _('WASTE')
            elif move.picking_id.type == 'return':
                res[move.id] = _('RETURN')

        return res

    def get_moves_in_location(self, cr, uid, location_id, prodlot_id, qty = 0.0, id = False):
        """returns the move in location"""
        moves = super(stock_move, self).get_moves_in_location(cr, uid, location_id, prodlot_id, qty=qty, id=id)

        if moves:
            ids_to_remove = []
            for move in self.browse(cr, uid, moves):
                if move.location_dest_id.usage == 'elimination':
                    ids_to_remove.append(move.id)
            ids = list(set(moves) - set(ids_to_remove))
            return ids
        else:
            return moves

    def _default_location_destination(self, cr, uid, context=None):
        """ Gets default address of partner for destination location
        @return: Address id or False
        """
        if context is None:
            context = {}
            
        if context.get('move_line', []):
            if context['move_line'][0]:
                if isinstance(context['move_line'][0], (tuple, list)):
                    return context['move_line'][0][2] and context['move_line'][0][2].get('location_dest_id',False)
                else:
                    move_list = self.pool.get('stock.move').read(cr, uid, context['move_line'][0], ['location_dest_id'])
                    return move_list and move_list['location_dest_id'][0] or False

        if context.get('address_out_id', False):
            property_out = self.pool.get('res.partner.address').browse(cr, uid, context['address_out_id'], context).partner_id.property_stock_customer
            return property_out and property_out.id or False
        if context.get('address_return_id', False):
            property_out = self.pool.get('res.partner.address').browse(cr, uid, context['address_return_id'], context).partner_id.property_stock_returns
            return property_out and property_out.id or False
        
        return False

    def _default_location_source(self, cr, uid, context=None):
        """ Gets default address of partner for source location
        @return: Address id or False
        """
        if context is None:
            context = {}

        if context.get('move_line', []):
            try:
                return context['move_line'][0][2]['location_id']
            except:
                pass

        if context.get('address_in_id', False):
            part_obj_add = self.pool.get('res.partner.address').browse(cr, uid, context['address_in_id'], context=context)
            if part_obj_add.partner_id:
                return part_obj_add.partner_id.property_stock_supplier.id
        if context.get('customer_address_id', False):
            part_obj_add = self.pool.get('res.partner.address').browse(cr, uid, context['customer_address_id'], context=context)
            if part_obj_add.partner_id:
                return part_obj_add.partner_id.property_stock_customer.id
            
        return False

    def _check_prodlot_blocked(self, cr, uid, ids):
        """checks if prodlot is blocked and is trying move"""
        for move in self.browse(cr, uid, ids):
            if move.prodlot_id and move.prodlot_id.blocked and move.state in ['assigned', 'done'] and move.location_dest_id.usage != 'elimination':
                return False
        return True

    _columns = {
                'towaste': fields.boolean('Eliminated', readonly=True),
                }

    _defaults = {
        'location_id': _default_location_source,
        'location_dest_id': _default_location_destination,
    }

    _constraints = [(_check_prodlot_blocked, _('Cannot move a blocked production lot to internal or customer location'), ['blocked'])
    ]

    def eval_onchange_lot_value(self, cr, uid, res, prodlot_id=False):
        """check prodlot_id in on_dhanges value"""
        prodlot = prodlot_id or ((res.get('value') and res['value'].get('prodlot_id')) and res['value']['prodlot_id'] or False)
        if res.get('warning', False):
            return res
        elif prodlot:
            obj_prodlot_id = self.pool.get('stock.production.lot').browse(cr, uid, prodlot)
            if obj_prodlot_id.in_alert:
                res['warning'] = {
                    'title': _('Production Lot in Alert!'),
                    'message': _('This production lot is on alert because any of its compounds are in poor conditions.'),
                        }
                return {'warning': res['warning'], 'value': res.get('value') and res['value'] or {}}
            elif obj_prodlot_id.blocked:
                res['warning'] = {
                    'title': _('Production Lot Blocked!'),
                    'message': _('This production lot is blocked because it is poor conditions.'),
                        }
                return {'warning': res['warning'], 'value': res.get('value') and res['value'].update({'prodlot_id': None}) or {'prodlot_id': None}}
        return res

    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False, loc_id=False, product_id=False, uom_id=False, context=None):
        """overwrites this event for shows a warning if the production lot selected is on alert"""
        if context is None: context = {}
        if not prodlot_id or not loc_id:
            return {}
        
        res = super(stock_move, self).onchange_lot_id(cr, uid, ids, prodlot_id = prodlot_id, product_qty = product_qty, loc_id = loc_id, product_id=product_id, uom_id=uom_id, context = context)
        return self.eval_onchange_lot_value(cr, uid, res, prodlot_id)

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, address_id=False, prod_qty=0.0, prodlot_id=False):
        """Extends this event checking prodlot obtained"""
        res = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, address_id)

        return self.eval_onchange_lot_value(cr, uid, res)

    def onchange_location_id(self, cr, uid, ids, product_id = False, location_id = False, dummy = False, product_qty=False, product_uom_id=False):
        """event fires when changes the location, checks the location and return a default production lot for this location"""
        res = super(stock_move, self).onchange_location_id(cr, uid, ids,product_id,location_id,dummy,product_qty,product_uom_id)

        return self.eval_onchange_lot_value(cr, uid, res)

    def action_done(self, cr, uid, ids, context=None):
        """overwrites this method for that to waste product be marked that eliminated"""
        for move in self.browse(cr, uid, ids):
            if move.location_dest_id.id == move.product_id.product_tmpl_id.property_waste.id:
                self.write(cr, uid, [move.id], {'towaste': True})
        return super(stock_move, self).action_done(cr, uid, ids, context)

stock_move()
