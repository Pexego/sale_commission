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

"""reasons to block production lots"""

from osv import osv, fields
import netsvc
import time
from tools.translate import _

class block_prodlot_cases(osv.osv):
    """reasons to block production lots"""
    _name = "block.prodlot.cases"
    _description = "Blockade cases"

    _columns = {
            'name': fields.char('Name', size=64, required=True, states={'confirm':[('readonly', True)]}),
            'description': fields.text('Description', required=True),
            'blocked_prodlots_ids': fields.many2many('stock.production.lot', 'blocked_prodlots_cases_ids', 'case_id', 'blocked_prodlot', 'Blocked Prodlots', states={'confirm':[('readonly', True)]}),
            'parent_block_prodlot': fields.many2one('stock.production.lot', 'Blockade Root', required=True, ondelete="set null", states={'confirm':[('readonly', True)]}),
            'state': fields.selection([('in_review', 'In Review'), ('confirm', 'Confirm'), ('cancelled', 'Cancelled')], 'State', required=True, readonly=True)
        }

    _defaults = {
            'state': 'in_review'
        }

    def send_blockade_case_notification(self, cr, uid, case_id, state = 'in_review'):
        """send a notification to Production Lots / Blockade Notifications users for blockade cases"""
        group_id = self.pool.get('res.groups').search(cr, uid, [('name', '=', 'Production Lots / Blockade Notifications')])

        if group_id:
            group_id = self.pool.get('res.groups').browse(cr, uid, group_id[0])
            
            obj_case_id = self.browse(cr, uid, case_id)
            #get a string comma list from object case prodlots collection
            # pylint: disable-msg=W0141
            lots_affected_names = u','.join(map(str, map(lambda x:x.name, obj_case_id.blocked_prodlots_ids)))

            if state == 'in_review':
                message = _("New production lots in review, will raise a warning meanwhile be in this state.\n\nLots names: %s\n\nBlockade Description: %s\n\n \
                        Blockade was raised from production_lot: %s.") % (lots_affected_names, obj_case_id.description, obj_case_id.parent_block_prodlot.name)
            else:
                message = _("New production lots blocked. Now not can you use this prodlots definitely.\n\nLots names: %s\n\nBlockade Description: %s\n\n \
                        Blockade was raised from production_lot: %s.") % (lots_affected_names, obj_case_id.description, obj_case_id.parent_block_prodlot.name)

            for user in group_id.user_ids:
                self.pool.get('res.request').create(cr, uid, {
                        'name': _("Blockade Case %s: %s") % (obj_case_id.id, obj_case_id.name),
                        'body': message,
                        'state': 'waiting',
                        'act_from': uid,
                        'act_to': user.id,
                        'ref_doc1': 'block.prodlot.cases,%d' % (obj_case_id.id,),
                        'priority': '2'
                    })

            return True

        return False

    def confirm_blockade_case(self, cr, uid, ids, context = None):
        """confirm blockade case and block definitely prodlots in alert affected by case"""
        if context is None: context = {}

        if isinstance(ids, (int, long)):
            ids = [ids]

        for obj_block_prodlot_case_id in self.browse(cr, uid, ids):
            created_move_ids = []
            for obj_blocked_prodlot_id in obj_block_prodlot_case_id.blocked_prodlots_ids:
                #searches if prodlots have other blockade cases that interrumpt his blockade
                cr.execute("select * from blocked_prodlots_cases_ids inner join block_prodlot_cases on id = case_id \
                    where blocked_prodlot = %s and case_id != %s and state not in ('confirm','cancelled')", (obj_blocked_prodlot_id.id, obj_block_prodlot_case_id.id))

                #if prodlot have another blockade cases in review it cannot block
                if cr.rowcount:
                    continue

                obj_real_report_prodlots_ids = self.pool.get('stock.report.prodlots').search(cr, uid, [('prodlot_id', '=', obj_blocked_prodlot_id.id),('qty','>',0)])

                for obj_real_report_prodlots_id in self.pool.get('stock.report.prodlots').browse(cr, uid, obj_real_report_prodlots_ids):

                    if obj_real_report_prodlots_id.location_id.usage not in ('internal'):
                        continue

                    move_id = self.pool.get('stock.move').create(cr, uid, {
                                'product_uom': obj_real_report_prodlots_id.product_id.uom_id.id,
                                'date' : time.strftime("%Y-%m-%d"),
                                'date_expected' : time.strftime("%Y-%m-%d"),
                                'prodlot_id': obj_blocked_prodlot_id.id,
                                'product_qty': obj_real_report_prodlots_id.qty,
                                'location_id': obj_real_report_prodlots_id.location_id.id,
                                'product_id': obj_real_report_prodlots_id.product_id.id,
                                'name': _("BLOCK: ") + obj_real_report_prodlots_id.prodlot_id.name + obj_real_report_prodlots_id.location_id.name,
                                'state': 'draft',
                                'location_dest_id': obj_real_report_prodlots_id.product_id.product_tmpl_id.property_waste.id
                                })

                    created_move_ids.append(move_id)

                #for update block and in_alert store attribute
                self.pool.get('stock.production.lot').write(cr, uid, [obj_blocked_prodlot_id.id], {'date': time.strftime("%Y-%m-%d %H:%M:%S")})

            if created_move_ids:
                picking_id = self.pool.get('stock.picking').create(cr, uid, {
                                                    'origin': _("BLOCKCASE:") + str(obj_block_prodlot_case_id.id),
                                                    'state': 'draft',
                                                    'type': 'internal',
                                                    'move_type': 'direct',
                                                    })

                self.pool.get('stock.move').write(cr, uid, created_move_ids, {'picking_id': picking_id})

                wf_service = netsvc.LocalService("workflow")
                wf_service.trg_validate(uid, 'stock.picking', picking_id, 'button_confirm', cr)

            self.write(cr, uid, [obj_block_prodlot_case_id.id], {
                                                        'state': 'confirm'
                                                        })

            #send block notification to users
            self.send_blockade_case_notification(cr, uid, obj_block_prodlot_case_id.id, 'confirm')

            #for update block and in_alert store attribute
            self.pool.get('stock.production.lot').write(cr, uid, [x.id for x in obj_block_prodlot_case_id.blocked_prodlots_ids], {})
        return True

    def cancel_blockade_case(self, cr, uid, ids, context = None):
        """cancelled blockade cases"""
        if context is None: context = {}
        self.write(cr, uid, ids, {'state': 'cancelled'})
        for obj_block_prodlot_case_id in self.browse(cr, uid, ids):
            self.pool.get('stock.production.lot').write(cr, uid, [x.id for x in obj_block_prodlot_case_id.blocked_prodlots_ids], {})
        return True

    def write(self, cr, uid, ids, vals, context = None):
        """overwrites write method for update production lots when case updating"""
        if context is None: context = {}
        moves_to_update = []

        if isinstance(ids, (int, long)):
            ids = [ids]

        for obj_case_id in self.browse(cr, uid, ids):
            moves_to_update = list(set(moves_to_update + [x.id for x in obj_case_id.blocked_prodlots_ids]))

        res = super(block_prodlot_cases, self).write(cr, uid, ids, vals, context)

        self.pool.get('stock.production.lot').write(cr, uid, moves_to_update, {})

        return res

    def create(self, cr, uid, vals, context = None):
        """overwrites this method to send notification informative with context of in alert prodlots and case"""
        if context is None: context = {}
        case_id = super(block_prodlot_cases, self).create(cr, uid, vals, context=context)

        #send in_review notification
        self.send_blockade_case_notification(cr, uid, case_id, 'in_review')

        return case_id

    def unlink(self, cr, uid, ids, context = None):
        """overwrites unlink function to update prodlots_state"""
        if context is None: context = {}
        affected_lots = []
        
        for blockade_case_id in self.browse(cr, uid, ids):
            if blockade_case_id.state == 'confirm':
                raise osv.except_osv(_("Warning!"), _("Can't delete confirmed blockade case."))

            affected_lots.extend([x.id for x in blockade_case_id.blocked_prodlots_ids])

        res = super(block_prodlot_cases, self).unlink(cr, uid, ids, context = context)

        if affected_lots:
            self.pool.get('stock.production.lot').write(cr, uid, affected_lots, {})

        return res

block_prodlot_cases()

class stock_production_lot(osv.osv):
    """inherit object to add many2many relationship with block.prodlot.cases"""
    _inherit = "stock.production.lot"

    _columns = {
            'blocked_prodlots_cases_ids': fields.many2many('block.prodlot.cases', 'blocked_prodlots_cases_ids', 'blocked_prodlot', 'case_id', "Blockade Cases"),
    }

stock_production_lot()
