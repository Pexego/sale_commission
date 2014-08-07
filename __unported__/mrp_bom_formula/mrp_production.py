# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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
import math
from tools.translate import _

class mrp_production(osv.osv):

    _inherit = "mrp.production"

    def _eval_production_bom(self, cr, uid, ids, context=None):
        """Evals bom formulas"""
        if context is None:
            context = {}
            
        res = {}
        if isinstance(ids, (int,long)):
            ids = [ids]
        
        for production_id in self.browse(cr, uid, ids):
            if production_id.bom_id:
                #production_uom -> bom_uom
                lines_dict = {'P': self.pool.get('product.uom')._compute_qty(cr, uid, production_id.product_uom.id, production_id.product_qty, production_id.bom_id.product_uom.id)}
                for line in production_id.bom_id.bom_lines:
                  
                        c_sequence = production_id.move_lines and [x.product_qty for x in production_id.move_lines if x.product_id.id == line.product_id.id] or [x.product_qty for x in production_id.product_lines if x.product_id.id == line.product_id.id]

                        localdict = {
                            'C' + str(line.sequence): c_sequence and reduce(lambda x,y: x+y,c_sequence) or 1.0,
                            
                            
                        }

                        for field in line.product_id.product_fields_ids:
                            r = [eval('l.'+field.name,{'l':x[0]}) * x[1] for x in [(x.prodlot_id,x.product_qty) for x in production_id.move_lines if x.prodlot_id and x.product_id.id == line.product_id.id]]
                            localdict.update({'L'+str(line.sequence)+'A'+str(field.sequence):(r and c_sequence) and reduce(lambda x,y: x+y,r) / reduce(lambda x,y: x+y,c_sequence) or 0.0})


                        lines_dict.update(localdict)
                res[production_id.id] = lines_dict
            else:
                res[production_id.id] = {}

        return res

    def action_compute(self, cr, uid, ids, properties=[], context=None):
        """Computation of formulas"""
        res = super(mrp_production, self).action_compute(cr, uid, ids, properties = properties, context=context)

        local_dict = self._eval_production_bom(cr, uid, ids)

        for production in self.browse(cr, uid, ids):
            if production.bom_id:
                for line in production.product_lines:
                    bom_ids = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', line.product_id.id),('bom_id', '=', production.bom_id.id),('eval_type', '=', 'computed')])
                    if bom_ids:
                        bom = self.pool.get('mrp.bom').browse(cr, uid, bom_ids[0])
                        try:
                            qty = eval(bom.formula, local_dict[production.id])
                            if qty < 1 :
                                line.write({'product_qty': 1.0})
                            else:
                                line.write({'product_qty': math.ceil(qty)})
                        except ZeroDivisionError:
                            line.write({'product_qty': 1.0})

        return res

    def action_compute_formulas(self, cr, uid, ids, context=None, first=True):
        if context is None: context = {}

        local_dict = self._eval_production_bom(cr, uid, ids)

        for production in self.browse(cr, uid, ids):
            if production.bom_id:
                for line in production.move_lines:
                    bom_ids = self.pool.get('mrp.bom').search(cr, uid, [('product_id', '=', line.product_id.id),('bom_id', '=', production.bom_id.id),('eval_type', '=', 'computed')])
                    if bom_ids:
                        bom = self.pool.get('mrp.bom').browse(cr, uid, bom_ids[0])
                        try:
                            qty = eval(bom.formula, local_dict[production.id])
                            if qty < 0:
                                line.write({'product_qty': 1.0})
                                self._update_product_lines(cr, uid, production, line.product_id.id, 1.0)
                            else:
                                qty = math.ceil(qty)
                                lines = [x for x in production.move_lines if x.product_id == line.product_id]
                                #line_uom -> bom_uom
                                curr_qty = reduce(lambda x,y: x+y,[self.pool.get('product.uom')._compute_qty(cr, uid, x.product_uom.id, x.product_qty, bom.product_uom.id) for x in lines])

                                if curr_qty != qty:
                                    if line.product_id.track_production or line.product_id.track_all:
                                        for product_line in lines:
                                            if not product_line.prodlot_id:
                                                raise osv.except_osv(_("Warning!"), _("All moves for %s need lots.") % line.product_id.name)

                                        #base_uom -> bom_uom
                                        avail_qty = reduce(lambda x,y: x+y,[x.prodlot_id.stock_available for x in lines])
                                        avail_qty = bom.product_uom.uom_type == 'bigger' and avail_qty / bom.product_uom.factor or avail_qty * bom.product_uom.factor

                                        if qty > avail_qty:
                                            for product_line in lines:
                                                #base_uom -> product_line_uom
                                                wqty = product_line.product_uom.uom_type == 'bigger' and product_line.prodlot_id.stock_available / product_line.product_uom.factor or product_line.prodlot_id.stock_available * product_line.product_uom.factor
                                                product_line.write({'product_qty': wqty})
                                                self._update_product_lines(cr, uid, production, product_line.product_id.id, wqty)
                                            new_qty = qty - avail_qty
                                            new_move = self.pool.get('stock.move').copy(cr, uid, line.id, {'product_qty': self.pool.get('product.uom')._compute_qty(cr, uid, bom.product_uom.id, new_qty, line.product_uom.id),
                                                                                                            'state': 'assigned',
                                                                                                            'prodlot_id': False,
                                                                                                            'location_id': line.location_id.id,
                                                                                                            'location_dest_id': line.location_dest_id.id,
                                                                                                            })
                                            production.write({'move_lines': [(4, new_move)]})
                                        elif qty < avail_qty and len(lines) == 1:
                                            line.write({'product_qty': qty})
                                            self._update_product_lines(cr, uid, production, line.product_id.id, qty)
                                        elif qty < avail_qty and len(lines) > 1:
                                            raise osv.except_osv(_("Warning!"), _("You must configure quantities manually, to product %s because, you have more than one lot with availability, for providing %s as computed quantity.") % (line.product_id.name, str(qty)))
                                    else:
                                        for product_line in lines:
                                            product_line.write({'product_qty': qty / len(lines)})
                                            self._update_product_lines(cr, uid, production, product_line.product_id.id, qty / len(lines))

                        except ZeroDivisionError:
                            line.write({'product_qty': 1.0})
                            self._update_product_lines(cr, uid, production, line.product_id.id, 1.0)

        if first:
            self.action_compute_formulas(cr, uid, ids, context=context, first=False)

        return True

    def _update_product_lines(self, cr, uid, production, product_id, product_qty):
        for line in production.product_lines:
            if line.product_id.id == product_id:
                line.write({'product_qty': product_qty})

        return True

mrp_production()