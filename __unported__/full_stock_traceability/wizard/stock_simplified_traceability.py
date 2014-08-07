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
from tools.translate import _

class action_simplified_traceability(osv.osv_memory):
    """
    This class defines a function action_traceability for wizard

    """
    _name = "action.simplified.traceability"
    _description = "Action simplified traceability "

    def action_traceability(self, cr, uid, ids, context=None):
        """ It traces a simplification of the information of a product
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: List of IDs selected
        @param context: A standard dictionary
        @return: A dictionary of values
        """
        lot_id = ids
        if context is None:
            context = {}
        tree_type = context['type'] or 'move_history_simplified_up'
        field = context['field'] or 'prodlot_id'
        model = "valid.stock.moves"

        obj = self.pool.get(model)
        ids = obj.search(cr, uid, [(field, 'in',lot_id)])
        cr.execute("""select stock_move.id from stock_move inner join stock_production_lot
            on stock_move.prodlot_id = stock_production_lot.id where stock_move.id in %s and
            (stock_move.id not in (select child_id from stock_move_history_ids) or
            (is_mix = True and prodlot_id not in (select distinct prodlot_id from stock_move AS sm
            inner join stock_move_history_ids on sm.id = parent_id
            where child_id in (stock_move.id))) or production_id is not null)""", (tuple(ids),))

        ids = []
        for (parent_id,) in cr.fetchall():
            ids.append(parent_id)

        cr.execute('select id from ir_ui_view where model=%s and field_parent=%s and type=%s', (model, tree_type, 'tree'))
        view_id = cr.fetchone()[0]
        # pylint: disable-msg=W0141
        value = {
            'domain': "[('id','in',["+','.join(map(str, ids))+"])]",
            'name': ((tree_type=='move_history_simplified_up') and _('Upstream Simplified Traceability')) or _('Downstream Simplified Traceability'),
            'view_type': 'tree',
            'res_model': model,
            'field_parent': tree_type,
            'view_mode': 'tree',
            'view_id': (view_id,'View'),
            'type': 'ir.actions.act_window',
            'nodestroy':True,
        }

        return value

action_simplified_traceability()