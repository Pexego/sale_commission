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

from osv import osv

class partial_picking(osv.osv_memory):

    _inherit = 'stock.partial.picking'

    def get_picking_type(self, cr, uid, picking, context=None):
        if context is None: context = {}
        picking_type = picking.type

        if picking_type != "in":
            for move in picking.move_lines:
                if picking.type == 'in' and move.product_id.cost_method == 'lifo':
                    picking_type = 'in'
                    break
        return picking_type

    def do_partial(self, cr, uid, ids, context=None):
        """ Makes partial moves and pickings done.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param fields: List of fields for which we want default values
        @param context: A standard dictionary
        @return: A dictionary which of fields with values.
        """
        if context is None: context = {}
        res = super(partial_picking, self).do_partial(cr, uid, ids, context=context)
        pick_obj = self.pool.get('stock.picking')

        picking_ids = context.get('active_ids', False)
        partial = self.browse(cr, uid, ids[0], context=context)

        for pick in pick_obj.browse(cr, uid, picking_ids, context=context):
            picking_type = self.get_picking_type(cr, uid, pick, context=context)
            moves_list = picking_type == 'in' and partial.move_ids or []

            for move in moves_list:
                if move.product_id.cost_method == 'lifo':
                    self.pool.get('product.product').write(cr, uid, [move.product_id.id],  {'standard_price': move.cost})

        return res

partial_picking()