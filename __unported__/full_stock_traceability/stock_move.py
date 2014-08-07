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

"""Allows trace all moves"""

from osv import osv, fields
from tools.translate import _
import time
import netsvc

def reverse_list( item_x, item_y ):
    """ordered a list of ids descently"""
    if item_x > item_y:
        rst = -1
    elif item_x < item_y:
        rst = 1
    else :
        rst = 0
    return rst

class stock_move(osv.osv):
    """Allows trace all moves"""

    _inherit = 'stock.move'

    def get_move_type(self, cr, uid, ids, context=None):
        """return the type of moves"""
        if context is None: context = {}
        res = {}

        for move in self.browse(cr, uid, ids):
            if move.picking_id and move.picking_id.type != 'internal':
                if move.picking_id.type == 'in':
                    res[move.id] = _('IN')
                elif move.picking_id.name and 'return' in move.picking_id.name:
                    res[move.id] = _('RETURN')
                elif move.picking_id.type == 'out':
                    res[move.id] = _('OUT')
                
            else:
                if move.location_dest_id.usage == 'customer':
                    res[move.id] = _('OUT')
                elif move.virtual and move.location_dest_id.usage == 'intermediate':
                    res[move.id] = _('TO MIX')
                elif move.prodlot_id and move.location_id.usage == 'intermediate' and move.prodlot_id.is_mix:
                    res[move.id] = _('MIX')
                elif move.scrapped:
                    res[move.id] = _('SCRAP')
                elif move.location_dest_id.usage == 'inventory':
                    res[move.id] = _('INVENTORY')
                elif move.location_id.usage == 'inventory':
                    res[move.id] = _('FROM INVENTORY')
                elif move.location_dest_id.usage == 'production':
                    res[move.id] = _('PRODUCTION')
                elif move.production_id:
                    res[move.id] = _('PRODUCTION FINAL MOVE')
                elif move.location_dest_id.usage == 'procurement':
                    res[move.id] = _('PROCUREMENT')
                else:
                    res[move.id] = _('INTERNAL')
        return res

    def _get_supplier(self, cr, uid, ids, field_name, arg, context):
        """gets the name of the supplier"""
        res = {}
        for move in self.browse(cr, uid, ids):
            res[move.id] = None
            if move.location_id.name == 'Suppliers':
                if move.picking_id and move.picking_id.address_id:
                    res[move.id] = move.picking_id.address_id.partner_id.name
        return res

    _columns = {
            'supplier': fields.function(_get_supplier, method=True, string="Supplier", type='char', size=255, store = True),
            'expiry_date': fields.related('prodlot_id', 'life_date', string='Expiry date', readonly=True, type='datetime'),
            'consumed_date': fields.datetime('Consumed date'),
            'virtual' : fields.boolean('Virtual Move', help="A virtual move, is an internal move necessary for follow-up the traceability")
        }

    def _check_location(self, cr, uid, ids, context=None):
        """checks if the location only acepts mixes and if the product is miscible"""
        for move in self.browse(cr, uid, ids):
            if move.location_dest_id.miscible_location and not move.product_id.miscible:
                return False
            elif move.product_id.miscible and not move.location_dest_id.miscible_location and move.location_dest_id.usage == 'internal' and move.state not in ('draft','waiting','confirmed'):
                return False
        return True

    def _check_tracking_all(self, cr, uid, ids, context=None):
        """ Checks if production lot is assigned to stock move or not.
        @return: True or False
        """
        for move in self.browse(cr, uid, ids, context=context):
            if not move.prodlot_id and move.state == 'done' and move.product_id.track_all:
                return False
        return True

    _constraints = [
        (_check_location, _('Location not valid for this product'), ['location_dest_id']),
        (_check_tracking_all,
            _('You must assign a production lot for this product'),
            ['prodlot_id'])
    ]

    def _create_move_mix(self, cr, uid, data):
        """creates the move for the mix"""
        #creates new production lot number
        if data['obj_virtual_move_inlocation'].product_id.sequence_id:
            production_lot_number = self.pool.get('ir.sequence').get_id(cr, uid, data['obj_virtual_move_inlocation'].product_id.sequence_id.id)
        else:
            raise osv.except_osv(_(u'Error!'), _(u"Please, configure lot sequence number in product %s." % data['obj_virtual_move_inlocation'].product_id.name))

        #creates an object with this production lot number
        mix_vals = {
        'name' : production_lot_number,
        'product_id' : data['obj_virtual_move_tomix'].product_id.id,
        'is_mix' : 1,
        }

        if data['obj_virtual_move_tomix'].product_uom.category_id.id != data['obj_virtual_move_inlocation'].product_uom.category_id.id:
            raise osv.except_osv(_(u'Error!'), _(u"Moves to mix have different categories of uoms."))

        uom_base_id = data['obj_virtual_move_tomix'].product_id.uom_id.id

        if data['obj_virtual_move_tomix'].product_uom.id != uom_base_id:
            tomix_qty = self.pool.get('product.uom')._compute_qty(cr, uid, data['obj_virtual_move_tomix'].product_uom.id, data['obj_virtual_move_tomix'].product_qty, uom_base_id)
        else:
            tomix_qty = data['obj_virtual_move_tomix'].product_qty

        if data['obj_virtual_move_inlocation'].product_uom.id == uom_base_id:
            inlocation_qty = self.pool.get('product.uom')._compute_qty(cr, uid, data['obj_virtual_move_inlocation'].product_uom.id, data['obj_virtual_move_inlocation'].product_qty, uom_base_id)
        else:
            inlocation_qty = data['obj_virtual_move_inlocation'].product_qty

        #create mix lot
        production_lot_number_id = self.pool.get('stock.production.lot').create(cr, uid, mix_vals)

        values = {
          'product_uom' : uom_base_id,
          'date' : data['obj_virtual_move_tomix'].date_expected,
          'product_qty' : tomix_qty + inlocation_qty,
          'location_id' : data['obj_virtual_move_tomix'].product_id.product_tmpl_id.property_mix.id,
          'product_id' : data['obj_virtual_move_inlocation'].product_id.id,
          'name' : 'M:' + production_lot_number,
          'date_expected' : data['obj_virtual_move_tomix'].date_expected,
          'state' : 'done',
          'location_dest_id' : data['destination'],
          'prodlot_id' : production_lot_number_id,
        }
        #creates the mix move
        new_id = self.create(cr, uid, values)

        self.write(cr, uid, [data['obj_virtual_move_tomix'].id, data['obj_virtual_move_inlocation'].id], {'move_dest_id': new_id})
        return new_id

    def _create_virtual_moves(self, cr, uid, obj_move_id, lot):
        """creates the virtual move for the product to mix because need this move that stock decrease"""
        #creates the virtual move from in location move
        values = {
          'product_uom' : lot.product_id.uom_id.id,
          'product_uos_qty' : lot.product_id.uom_id.uom_type == 'bigger' and  lot.stock_available / lot.product_id.uom_id.factor or lot.stock_available * lot.product_id.uom_id.factor,
          'date' : time.strftime("%Y-%m-%d"),
          'product_qty' : lot.product_id.uom_id.uom_type == 'bigger' and  lot.stock_available / lot.product_id.uom_id.factor or lot.stock_available * lot.product_id.uom_id.factor,
          'product_uos' : lot.product_id.uom_id.id,
          'location_id' : obj_move_id.location_dest_id.id,
          'product_id' : lot.product_id.id,
          'name' : 'M:' + str(obj_move_id.location_dest_id.id) + 'TOMVS' + time.strftime("%Y-%m-%d"),
          'date_expected' : time.strftime("%Y-%m-%d"),
          'state' : 'done',
          'location_dest_id' : lot.product_id.product_tmpl_id.property_mix.id,
          'prodlot_id' : lot.id,
          'virtual' : 1,
        }
        virtual_move_from_inlocation_id = self.create(cr, uid, values)

        #movimiento que entra

        vals = {
            'product_uom' : obj_move_id.product_uom.id,
            'product_uos_qty' : obj_move_id.product_uos_qty,
            'date' : time.strftime("%Y-%m-%d"),
            'product_qty' : obj_move_id.product_qty,
            'product_uos' : obj_move_id.product_uos and obj_move_id.product_uos.id or False,
            'location_id' : obj_move_id.location_dest_id.id,
            'product_id' : obj_move_id.product_id.id,
            'name' : 'M:' + str(obj_move_id.id) + 'TOMVS' + time.strftime("%Y-%m-%d"),
            'date_expected' : time.strftime("%Y-%m-%d"),
            'state' : 'done',
            'location_dest_id' : obj_move_id.product_id.product_tmpl_id.property_mix.id,
            'prodlot_id' : obj_move_id.prodlot_id.id,
            'virtual' : 1,
            }

        virtual_move_from_movetomix_id = self.create(cr, uid, vals)
        #dictionary with the params to return needed for create the mix (the object of the virtual moves and the real destination)
        data = {
                'obj_virtual_move_inlocation' : self.browse(cr, uid, virtual_move_from_inlocation_id),
                'obj_virtual_move_tomix' : self.browse(cr, uid, virtual_move_from_movetomix_id),
                'destination' : obj_move_id.location_dest_id.id,
                }

        return data

    def _check_and_mix(self, cr, uid, move, context=None):
        """Mixes the move as argument"""
        if move.product_id.miscible and move.location_dest_id.miscible_location:
            location = self.pool.get('stock.location').browse(cr, uid, move.location_dest_id.id, context={'product_id': move.product_id.id})
            if location.stock_real:
                lots_inside = self.pool.get('stock.location').get_lots_inside(cr, uid, location.id, move.product_id.id, context=context)

                if len(lots_inside) > 1:
                    raise osv.except_osv(_('Error!'), _("Invalid miscible location. Location has more that one lot."))
                elif not lots_inside:
                    raise osv.except_osv(_('Error!'), _("Invalid miscible location. Location has stock but it hasn't lot."))

                lot = self.pool.get('stock.production.lot').browse(cr, uid, lots_inside[0], context={'location_id': move.location_dest_id.id})
                data = self._create_virtual_moves(cr, uid, move, lot)
                self._create_move_mix(cr, uid, data)
                return True

        return False
    
    def get_moves_in_location(self, cr, uid, location_id, prodlot_id, qty = 0.0, id = False):
        """returns the moves in location"""
        moves = []
        if not prodlot_id:
            return moves

        domain = [('location_dest_id', '=', location_id), ('prodlot_id', '=', prodlot_id), ('location_id', '!=', location_id)]
        if id:
            domain.append(('id','<',id))

        ids = self.search(cr, uid, domain)
        if len(ids) == 1:
            moves = ids
        elif len(ids) == 0:
            return moves
        else:
            ids_to_remove = []
            for move in self.browse(cr, uid, ids):
                m_qty = move.product_qty
                for child_move in move.move_history_ids:
                    m_qty -= child_move.product_qty
                if m_qty <= 0: #if move is consumed
                    ids_to_remove.append(move.id)
            if ids_to_remove:
                ids = list(set(ids) - set(ids_to_remove))

            if qty:
                #if there are many items with that params, go on with one param more
                domain.append(('product_qty', '>=', qty))
                move_id = self.search(cr, uid, domain)
                
                if len(move_id) == 1:
                    moves = move_id
                elif len(move_id) > 1:
                    moves = [move_id[len(move_id)-1]]
                else:
                    #check if stock in location are in more that one move
                    select_moves = []
                    move_qty = qty
                    ids.sort(reverse_list)
                    for obj_move_id in self.browse(cr, uid, ids):
                        move_qty = move_qty - obj_move_id.product_qty
                        select_moves.append(obj_move_id.id)
                        if move_qty <= 0:
                            break
                    moves = select_moves

        return moves

    def recompute_parent_moves(self, cr, uid, ids, context=None):
        """recomputes parent moves for traceability"""
        if context is None: context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        for move in self.browse(cr, uid, ids, context=context):
            parent_moves = self.get_moves_in_location(cr, uid, move.location_id.id, move.prodlot_id and move.prodlot_id.id or False, qty=move.product_qty, id=move.id)
            if parent_moves:
                super(stock_move, self).write(cr, uid, [move.id], {'move_history_ids2': [(6, 0, parent_moves)]})
            else:
                if not move.production_id:
                    cr.execute("delete from stock_move_history_ids where child_id = %s and parent_id != %s" % (str(move.id),str(move.move_dest_id and move.move_dest_id.id or move.id)))

            if move.move_dest_id and move.move_dest_id.id not in [x.id for x in move.move_history_ids]:
                super(stock_move, self).write(cr, uid, [move.id], {'move_history_ids': [(4, move.move_dest_id.id)]})

        return True

    def create(self, cr, uid, vals, context=None):
        """Extends create method to recompute parent moves"""
        if context is None: context = {}
            
        res = super(stock_move, self).create(cr, uid, vals, context=context)

        self.recompute_parent_moves(cr, uid, [res])

        return res

    def write(self, cr, uid, ids, vals, context=None):
        """Extends write method to recompute parent moves and check mix"""
        if context is None: context = {}
        done = False

        if vals.get('state', False) and vals['state'] == 'done':
            del vals['state']
            done = True

        res = super(stock_move, self).write(cr, uid, ids, vals, context=context)

        if done:
            for move in self.browse(cr, uid, ids):
                self._check_and_mix(cr, uid, move)

            super(stock_move, self).write(cr, uid, ids, {'state': 'done'})

        self.recompute_parent_moves(cr, uid, ids)

        return res

    def onchange_location_id(self, cr, uid, ids, product_id = False, location_id = False, dummy = False, product_qty=False, product_uom_id=False):
        """event fires when changes the location, checks the location and return a default production lot for this location"""
        #if not location or product not return anything
        if not location_id or not product_id:
            return {}
        #if the product quantity needed not exist or is <= 0, set the product quantity to one because is 0 or less not return a valid default_prodlot
        if not product_qty or product_qty <= 0:
            product_qty = 1

        if product_uom_id:
            uom_id = self.pool.get('product.product').browse(cr, uid, product_id).uom_id.id
            product_qty = self.pool.get('product.uom')._compute_qty(cr, uid, product_uom_id, product_qty, uom_id)

        #searches the default prodlot for this location and this product
        default_prodlot, split = self.pool.get('stock.production.lot').get_default_production_lot(cr, uid, location_id, product_id, product_qty, deep = False)
        #if not return anything, raises an alert because no exist a production lot and must be created
        if not default_prodlot and not split:
            warning = {
                'title': _('Alert !'),
                'message': _('There are not any production lot in this location, must be created.')
                }
            return {'warning': warning}
        elif split:
            result = {
                'prodlot_id': default_prodlot or None
            }
            warning = {'title': _('Advice'),
                       'message': _('You could split the move to satisfy the quantity needed.')}
            return {'value': result, 'warning': warning}
        elif self.pool.get('stock.location').browse(cr, uid, location_id).usage == 'supplier':
            result = {
                    'prodlot_id': None,
                    }
            return {'value': result}
        else:
            result = {
                    'prodlot_id': default_prodlot,
                    }
            return {'value': result}
        return {}

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, address_id=False, prod_qty=0.0, prodlot_id=False):
        """Extends this event to load more data for this product"""
        #return a value with the product and the product_uom, if not product return nothing
        parent_result = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, address_id)
        if not parent_result:
            #No hay product_id
            return parent_result
        #gets the object of the product
        obj_product_id = self.pool.get('product.product').browse(cr, uid, prod_id)

        #checks if this product is available in the location
        result = self.onchange_location_id(cr, uid, ids, product_id = prod_id, location_id = loc_id, product_qty = prod_qty)
        if result.get('value', False) and not result.get('warning', False) and parent_result.get('value') and parent_result['value'].get('name'):
            if not prodlot_id:
                result['value']['name'] = parent_result['value']['name']
            else:
                result['value']['name'] = parent_result['value']['name'] + " (" + self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id).name + ")"
            result['value']['product_uom'] = parent_result['value']['product_uom']
            return result

        if not result.get('value', False):
            result['value'] = {}

        result['value'] = {
                    'product_uom': obj_product_id.product_tmpl_id.uom_id.id
                  }

        if prodlot_id:
            result['value']['name'] = obj_product_id.product_tmpl_id.name + " (" + self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id).name + ")"
        else:
            result['value']['name'] = obj_product_id.product_tmpl_id.name
            
        return result

    def onchange_lot_id(self, cr, uid, ids, prodlot_id=False, product_qty=False, loc_id=False, product_id=False, uom_id=False, context=None):
        """extends this event for change the name by product code + prodlot name"""
        res = super(stock_move, self).onchange_lot_id(cr, uid, ids, prodlot_id = prodlot_id, product_qty = product_qty, loc_id = loc_id, product_id=product_id, uom_id=uom_id, context = context)
        if res.get('warning', False):
            prodlot = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id, context=context)
            location = self.pool.get('stock.location').browse(cr, uid, loc_id, context=context)
            uom = self.pool.get('product.uom').browse(cr, uid, uom_id, context=context)
            amount_actual = uom.uom_type == 'bigger' and prodlot.stock_available / uom.factor or prodlot.stock_available * uom.factor

            if (location.usage == 'internal') and (product_qty > (amount_actual or 0.0)):
                res['warning'] = {
                    'title': _('Insufficient Stock in Lot !'),
                    'message': _('You are moving %.2f %s products but only %.2f %s available in this lot.') % (product_qty, uom.name, amount_actual, uom.name)
                }
            else:
                res = {}
        else:
            if prodlot_id:
                prodlot_obj_id = self.pool.get('stock.production.lot').browse(cr, uid, prodlot_id)
                if not 'value' in res:
                    res['value'] = {}
                res['value']['name'] = prodlot_obj_id.product_id.product_tmpl_id.name + " (" + prodlot_obj_id.name + ")"

            return res
        return res

    def _create_lot(self, cr, uid, ids, product_id, prefix=False):
        """Overwrites this method to set product sequence to lot opassing product in context"""
        prodlot_obj = self.pool.get('stock.production.lot')
        prodlot_id = prodlot_obj.create(cr, uid, {'prefix': prefix, 'product_id': product_id}, context={'product_id': product_id})
        return prodlot_id

    def action_cancel(self, cr, uid, ids, context=None):
        """Removes move_dest_id to avoid force assign"""
        if context is None:
            context = {}

        self.write(cr, uid, ids, {'move_dest_id': False})

        return super(stock_move, self).action_cancel(cr, uid, ids, context=context)

    def move_reserve_split(self, cr, uid, ids, context=None):
        """split move in move with procurements to satisfy quantity needed"""
        if context is None: context = {}
        new_moves = []
        wf_service = netsvc.LocalService("workflow")

        for move in self.browse(cr, uid, ids, context=context):
            quantity = self.pool.get('product.uom')._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id)
            tlots = self.pool.get('stock.production.lot').get_all_parent_location(cr, uid, move.location_id, move.product_id.id, quantity, deep=True)

            if tlots:
                qty_towrite = self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, quantity, move.product_uom.id)
                self.write(cr, uid, [move.id], {'prodlot_id': tlots[0][0],
                                                'location_id': tlots[0][1],
                                                'product_qty': tlots[0][2] >= quantity and qty_towrite or self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, tlots[0][2], move.product_uom.id)
                                                })
                #writes consumed move if exists
                if move.move_dest_id and not move.move_dest_id.production_id and move.move_dest_id.state not in ['cancel', 'done']:
                    self.write(cr, uid, [move.move_dest_id.id], {'prodlot_id': tlots[0][0],
                                                'location_id': move.location_dest_id.id,
                                                'product_qty': tlots[0][2] >= quantity and qty_towrite or self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, tlots[0][2], move.product_uom.id)
                                                })

                procurement_ids = self.pool.get('procurement.order').search(cr, uid, [('move_id', '=', move.id)])
                proc_obj = False
                if procurement_ids:
                    proc_obj = self.pool.get('procurement.order').browse(cr, uid, procurement_ids[0])

                if tlots[0][2] < quantity:
                    move_qty = quantity - tlots[0][2]
                    tlots.pop(0)

                    for record in tlots:
                        if move_qty == 0.0:
                            break;

                        if record[2] >= move_qty:
                            qty_towrite = move_qty
                        else:
                            qty_towrite = record[2]

                        qty_towrite = self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, qty_towrite, move.product_uom.id)

                        if move.move_dest_id:
                            #creates new picking move
                            move_dest_id = self.create(cr, uid, {
                                'name': move.name,
                                'date': move.date,
                                'product_id': move.product_id.id,
                                'product_qty': qty_towrite,
                                'product_uom': move.product_uom.id,
                                'product_uos_qty': qty_towrite,
                                'product_uos': move.product_uom.id,
                                'location_id': move.product_id.not_do_procurement and record[1] or move.location_dest_id.id,
                                'location_dest_id': move.move_dest_id and move.move_dest_id.location_dest_id.id or move.product_id.product_tmpl_id.property_stock_production.id,
                                'move_dest_id': move.move_dest_id and move.move_dest_id.move_dest_id and move.move_dest_id.move_dest_id.id or False,
                                'state': 'waiting',
                                'company_id': move.company_id.id,
                                'prodlot_id': record[0]
                            })
                            new_moves.append(move_dest_id)
                        #creates related production_move
                        move_id = self.create(cr, uid, {
                            'name': move.name,
                            'picking_id': (not move.product_id.not_do_procurement and move.picking_id) and move.picking_id.id or False,
                            'product_id': move.product_id.id,
                            'product_qty': qty_towrite,
                            'product_uom': move.product_uom.id,
                            'product_uos_qty': qty_towrite,
                            'product_uos': move.product_uom.id,
                            'date': move.date,
                            'move_dest_id': move.move_dest_id and move_dest_id or False,
                            'location_id': record[1],
                            'location_dest_id': move.location_dest_id.id,
                            'state': 'waiting',
                            'company_id': move.company_id.id,
                            'prodlot_id': record[0]
                        })
                        #creates procurement
                        if proc_obj and not move.product_id.not_do_procurement:
                            proc_id = self.pool.get('procurement.order').create(cr, uid, {
                                'name': u'Split: ' + proc_obj.name,
                                'origin': proc_obj.origin,
                                'date_planned': proc_obj.date_planned,
                                'product_id': move.product_id.id,
                                'product_qty': qty_towrite,
                                'product_uom': move.product_uom.id,
                                'product_uos_qty': qty_towrite,
                                'product_uos': move.product_uom.id,
                                'location_id': record[1],
                                'procure_method': move.product_id.procure_method,
                                'move_id': move_id,
                                'company_id': move.company_id.id,
                            })
                            wf_service.trg_validate(uid, 'procurement.order', proc_id, 'button_confirm', cr)

                        if record[2] >= move_qty:
                            move_qty = 0.0
                        else:
                            move_qty -= record[2]

        return new_moves

    def action_consume(self, cr, uid, ids, quantity_orig, location_id=False, context=None):
        """extends this method to manage miscible products"""
        if context is None: context = {}
        
        miscible_moves = [] #miscible moves manages separate of ids
        miscible_res = [] #new miscible moves

        if quantity_orig <= 0:
            raise osv.except_osv(_('Warning!'), _('Please provide Proper Quantity !'))

        for move in self.browse(cr, uid, ids, context=context):
            quantity = self.pool.get('product.uom')._compute_qty(cr, uid, move.product_uom.id, quantity_orig, move.product_id.uom_id.id)
            if (move.product_id.miscible or move.product_id.not_do_procurement) and move.product_id.track_all:
                miscible_moves.append(move.id)

                move_qty = self.pool.get('product.uom')._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id)
                if move_qty <= 0:
                    raise osv.except_osv(_('Error!'), _('Can not consume a move with negative or zero quantity !'))

                quantity_rest = move_qty
                quantity_rest -= quantity
                move_uos_qty = self.pool.get('product.uom')._compute_qty(cr, uid, move.product_uos and move.product_uos.id or move.product_uom.id, move.product_uos_qty, move.product_id.uom_id.id)
                uos_qty_rest = (quantity_rest / move_qty) * move_uos_qty

                if quantity_rest <= 0:
                    quantity_rest = 0
                    uos_qty_rest = 0
                    quantity = move_qty

                uos_qty = (quantity / move_qty) * move_uos_qty

                if quantity_rest > 0:
                    #new move
                    default_val = {
                        'product_qty': self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, quantity, move.product_uom.id),
                        'product_uos_qty': self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, uos_qty, move.product_uom.id),
                        'state': move.state,
                        'location_id': location_id or move.location_id.id,
                    }
                    #if not prodlot, tries to obtain one
                    if not move.prodlot_id.id:
                        default_prodlot, prodlot_location, default_qty, split = self.pool.get('stock.production.lot').get_default_production_lot(cr, uid, default_val['location_id'], move.product_id.id, quantity, deep=True)
                        if not default_prodlot:
                            # in the case if doesn't get any prodlot
                            raise osv.except_osv(_('Error!'), _('You have to set a production lot for this move %s.') % move.product_id.name)
                        else:
                            default_val.update({
                                'prodlot_id': default_prodlot,
                                'location_id': prodlot_location
                            })

                    current_move = self.copy(cr, uid, move.id, default_val)
                    miscible_res.append(current_move)

                    # update the original move with rests
                    self.write(cr, uid, [move.id], {
                            'product_qty': self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, quantity_rest, move.product_uom.id),
                            'product_uos_qty': self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, uos_qty_rest, move.product_uom.id),
                        })

                    #searches productions with opriginal move
                    production_obj = self.pool.get('mrp.production')
                    production_ids = production_obj.search(cr, uid, [('move_lines', 'in', [move.id])])
                    #if found productions update them with new move
                    production_obj.write(cr, uid, production_ids, {'move_lines': [(4, current_move)]})
                else:
                    update_val = {
                            'product_qty' : self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, quantity, move.product_uom.id),
                            'product_uos_qty' : self.pool.get('product.uom')._compute_qty(cr, uid, move.product_id.uom_id.id, uos_qty, move.product_uom.id),
                            'location_id': location_id or move.location_id.id
                        }
                        
                    if not move.prodlot_id.id:
                        #if not prodlot tries to fin it else raises a warning
                        default_prodlot, prodlot_location, default_qty, split = self.pool.get('stock.production.lot').get_default_production_lot(cr, uid, update_val['location_id'], move.product_id.id, quantity, deep=True)
                        if not default_prodlot:
                            raise osv.except_osv(_('Error!'), _('You have to set a production lot for this move %s.') % move.product_id.name)
                        else:
                            update_val.update({
                                'prodlot_id': default_prodlot,
                                'location_id': prodlot_location
                            })

                    miscible_res.append(move.id)
                    #updates the move
                    self.write(cr, uid, [move.id], update_val)

            elif (not move.prodlot_id.id) and (move.product_id.track_all and location_id):
                raise osv.except_osv(_('Error!'), _('You have to set a production lot for this move. Product: %s') % move.product_id.name)

        # remove from ids miscible ids to call super with no manage ids
        ids = list(set(ids) - set(miscible_moves))
        res = super(stock_move, self).action_consume(cr, uid, ids, quantity_orig, location_id=location_id, context=context)

        if miscible_res:
            # if there are miscible moves tries to finished its
            self.action_done(cr, uid, miscible_res)
            res.extend(miscible_res)

            #tries force production with new misible_moves
            production_obj = self.pool.get('mrp.production')
            wf_service = netsvc.LocalService("workflow")
            production_ids = production_obj.search(cr, uid, [('move_lines', 'in', miscible_moves)])

            for prod in production_obj.browse(cr, uid, production_ids, context=context):
                if prod.state == 'confirmed':
                    production_obj.force_production(cr, uid, [prod.id])
                wf_service.trg_validate(uid, 'mrp.production', prod.id, 'button_produce', cr)

        return res

    def action_scrap(self, cr, uid, ids, quantity, location_id, context=None):
        """Extends action_scrap removing move_dest_id to scrapped moves"""
        if context is None: context = {}
        res = super(stock_move, self).action_scrap(cr, uid, ids, quantity, location_id, context=context)

        for move in self.browse(cr, uid, res):
            vals = {}
            if move.move_dest_id:
                vals['move_dest_id'] = False

                if move.move_dest_id.id in [x.id for x in move.move_history_ids]:
                    vals['move_history_ids'] = [(3, move.move_dest_id.id)]

                self.write(cr, uid, [move.id], vals)

        return res

    def force_assign(self, cr, uid, ids, context=None):
        """ Checks if it has lot and it can be assigned."""
        if context is None: context = {}

        if isinstance(ids, (int,long)):
            ids = [ids]

        for move in self.browse(cr, uid, ids, context=context):
            valid = True
            if move.location_dest_id.miscible_location and not move.product_id.miscible:
                valid = False
            elif move.product_id.miscible and not move.location_dest_id.miscible_location and move.location_dest_id.usage == 'internal':
                valid = False

            if valid:
                super(stock_move, self).force_assign(cr, uid, [move.id], context=context)

        return True
        

stock_move()