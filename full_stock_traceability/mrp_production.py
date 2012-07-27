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
import netsvc

class mrp_production(osv.osv):

    _inherit = 'mrp.production'

    def action_confirm(self, cr, uid, ids, context=None):
        """extends this method for managing no_procurement_moves"""
        if context is None: context = {}
        picking_id = super(mrp_production, self).action_confirm(cr, uid, ids, context=context)
        
        to_delete_moves = []
        procurements_to_delete = []
        
        picking_obj = self.pool.get('stock.picking').browse(cr, uid, picking_id)

        for move in picking_obj.move_lines:
            if move.product_id.miscible or move.product_id.not_do_procurement:
                #not procurement
                procurements = self.pool.get('procurement.order').search(cr, uid, [('move_id', '=', move.id)])
                if procurements:
                    procurements_to_delete.extend(procurements)
                    
                if move.move_dest_id:
                    self.pool.get('stock.move').write(cr, uid, [move.move_dest_id.id], {'location_id': move.product_id.product_tmpl_id.property_raw.id})
                    if move.move_dest_id.product_id.miscible:
                        self.pool.get('stock.move').write(cr, uid, [move.move_dest_id.id], {'state': 'assigned'})

                to_delete_moves.append(move.id)

            if move.product_id.track_all and not move.product_id.miscible:
                default_prodlot, prodlot_location, default_qty, split = self.pool.get('stock.production.lot').get_default_production_lot(cr, uid, move.location_id.id, move.product_id.id, self.pool.get('product.uom')._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id), deep=True)

                if split:
                    new_moves = self.pool.get('stock.move').move_reserve_split(cr, uid, [move.id])
                    for new_move in new_moves:
                        self.write(cr, uid, ids, {'move_lines': [(4, new_move)]})
                else:
                    vals = {}
                    if default_prodlot:
                        vals['prodlot_id'] = default_prodlot
                    if prodlot_location:
                        vals['location_id'] = prodlot_location

                    self.pool.get('stock.move').write(cr, uid, [move.id], vals)
                    if move.move_dest_id:
                        self.pool.get('stock.move').write(cr, uid, [move.move_dest_id.id], {'prodlot_id': default_prodlot})
                        if move.move_dest_id.product_id.not_do_procurement and prodlot_location:
                            self.pool.get('stock.move').write(cr, uid, [move.move_dest_id.id], {'location_id': prodlot_location})

        self.pool.get('stock.move').write(cr, uid, to_delete_moves, {'move_dest_id': False, 'state': 'draft'})
        self.pool.get('procurement.order').write(cr, uid, list(set(procurements_to_delete)), {'state': 'draft'})
        self.pool.get('procurement.order').unlink(cr, uid, list(set(procurements_to_delete)))
        self.pool.get('stock.move').unlink(cr, uid, to_delete_moves)

        picking_obj = self.pool.get('stock.picking').browse(cr, uid, picking_id)
        if not picking_obj.move_lines:
            wf_service = netsvc.LocalService("workflow")
            wf_service.trg_write(uid, 'stock.picking', picking_obj.id, cr)

        return picking_id

mrp_production()