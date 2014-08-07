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

"""extends create mix method"""

from osv import osv

class stock_move(osv.osv):

    _inherit = "stock.move"

    def _create_virtual_moves(self, cr, uid, obj_move_id, lot):
        """computes alcohol percente if it's necessary"""
        if obj_move_id.production_id:
            self.pool.get('mrp.production').action_compute_price(cr, uid, [obj_move_id.production_id.id])
            obj_move_id = self.pool.get('stock.move').browse(cr, uid, obj_move_id.id)

        return super(stock_move, self)._create_virtual_moves(cr, uid, obj_move_id, lot)

    def _create_move_mix(self, cr, uid, data):
        """extends create mix method"""
        new_id = super(stock_move, self)._create_move_mix(cr, uid, data)
        move = self.browse(cr, uid, new_id)

        uom_base_id = data['obj_virtual_move_tomix'].product_id.uom_id.id

        if data['obj_virtual_move_tomix'].product_uom.id != uom_base_id:
            tomix_qty = self.pool.get('product.uom')._compute_qty(cr, uid, data['obj_virtual_move_tomix'].product_uom.id, data['obj_virtual_move_tomix'].product_qty, uom_base_id)
        else:
            tomix_qty = data['obj_virtual_move_tomix'].product_qty

        if data['obj_virtual_move_inlocation'].product_uom.id == uom_base_id:
            inlocation_qty = self.pool.get('product.uom')._compute_qty(cr, uid, data['obj_virtual_move_inlocation'].product_uom.id, data['obj_virtual_move_inlocation'].product_qty, uom_base_id)
        else:
            inlocation_qty = data['obj_virtual_move_inlocation'].product_qty

        new_unit_price = (data['obj_virtual_move_tomix'].price + data['obj_virtual_move_inlocation'].price) / (tomix_qty + inlocation_qty)
        self.pool.get('stock.production.lot').write(cr, uid, [move.prodlot_id.id], {'unit_price': new_unit_price})

        return new_id


stock_move()