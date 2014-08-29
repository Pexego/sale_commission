# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) TODAY Pexego Sistemas Informáticos All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm
from openerp.tools.translate import _


class settled_invoice_wizard (orm.TransientModel):
    """settled.invoice.wizard"""

    _name = 'settled.invoice.wizard'
    _columns = {
        'journal_id': fields.many2one('account.journal', 'Target journal',
                                      required=True, select=1),
        'product_id': fields.many2one('product.product', 'Product for account',
                                      required=True, select=1),
        'mode': fields.selection([('line', 'for each invoice line settled'),
                                  ('invoice', 'for each sale invoice'),
                                  ('agent', 'summary for each agent')],
                                 'Invoice mode', required=True),
    }
    _defaults = {
    }

    def create_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data_pool = self.pool.get('ir.model.data')
        settlement_obj = self.pool.get('settlement')

        for o in self.browse(cr, uid, ids, context=context):
            res = settlement_obj.action_invoice_create(
                cr, uid, context['active_ids'],
                journal_id=o.journal_id.id, product_id=o.product_id.id,
                mode=o.mode, context=context)

        invoice_ids = res.values()

        action_model = False
        action = {}
        if not invoice_ids[0]:
            raise orm.except_orm(_('Error'), _('No Invoices were created'))

        # change state settlement
        settlement_obj.write(cr, uid, context['active_ids'],
                             {'state': 'invoiced'})

        action_model, action_id = data_pool.get_object_reference(
            cr, uid, 'account', "action_invoice_tree2")

        if action_model:
            action_pool = self.pool.get(action_model)
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = \
                "[('id','in', [" + ','.join(map(str, invoice_ids[0])) + "])]"
        return action

settled_invoice_wizard()
