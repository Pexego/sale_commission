# -*- coding: utf-8 -*-
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


class stock_picking(orm.Model):
    """
        Modificamos la creación de factura desde albarán para incluir el
       comportamiento de comisiones
    """

    _inherit = 'stock.picking'

    _columns = {
        'agent_ids': fields.many2many('sale.agent', 'sale_agent_clinic_rel',
                                      'agent_id', 'clinic_id', 'Agentes')
    }

    def _create_invoice_line_agent(self, cr, uid, ids, agent_id, commission_id):
        vals = {
            'agent_id': agent_id,
            'commission_id': commission_id,
            'settled': False
        }
        line_agent_id = self.pool.get('invoice.line.agent').create(cr, uid,
                                                                   vals)
        self.pool.get('invoice.line.agent').calculate_commission(
            cr, uid, [line_agent_id])
        return line_agent_id

    def _create_invoice_from_picking(self, cr, uid, picking, vals,
                                     context=None):
        '''
            Para linkear bien la factura a los envios parciales
        '''
        invoice_id = super(stock_picking, self)._create_invoice_from_picking(
            cr, uid, picking, vals, context=context)
        agent_id = picking.agent_ids and picking.agent_ids[0].id or False
        self.pool.get("account.invoice").write(cr, uid, [invoice_id],
                                               {'agent_id': agent_id})
        return invoice_id


class StockMove(orm.Model):

    _inherit = "stock.move"

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type,
                               context=None):
        res = super(StockMove, self).\
            _get_invoice_line_vals(cr, uid, move, partner, inv_type,
                                   context=context)
        list_ids = []
        if move.procurement_id.sale_line_id and not \
                move.procurement_id.sale_line_id.product_id.commission_exent:
            line = move.procurement_id.sale_line_id
            if not line.line_agent_ids:
                for so_comm in line.order_id.sale_agent_ids:
                    line_agent_id = self.pool['stock.picking'].\
                        _create_invoice_line_agent(cr, uid, [],
                                                   so_comm.agent_id.id,
                                                   so_comm.commission_id.id)
                    list_ids.append(line_agent_id)

            else:
                for l_comm in line.line_agent_ids:
                    line_agent_id = self.pool['stock.picking'].\
                        _create_invoice_line_agent(cr, uid, [],
                                                   l_comm.agent_id.id,
                                                   l_comm.commission_id.id)
                    list_ids.append(line_agent_id)
        res['commission_ids'] = [(6, 0, list_ids)]
        return res
