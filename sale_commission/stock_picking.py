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

    def _create_invoice_line_agent(self, cr, uid, ids, agent_id, commission_id,
                                   invoice_line_id):
        vals = {
            'agent_id': agent_id,
            'commission_id': commission_id,
            'settled': False,
            'invoice_line_id': invoice_line_id
        }
        line_agent_id = self.pool.get('invoice.line.agent').create(cr, uid,
                                                                   vals)
        self.pool.get('invoice.line.agent').calculate_commission(
            cr, uid, [line_agent_id])
        return line_agent_id

    def action_invoice_create(self, cr, uid, ids, journal_id, group=False,
                              type='out_invoice', context=None):
        invoices = super(stock_picking, self).action_invoice_create(
            cr, uid, ids, journal_id, group, type, context)
        for picking in self.browse(cr, uid, ids, context):
            for move_line in picking.move_lines:
                if move_line and move_line.procurement_id and \
                        move_line.procurement_id.sale_line_id and  \
                        move_line.procurement_id.sale_line_id.product_id.commission_exent is not True:
                    # line = move_line.sale_line_id
                    line = move_line.procurement_id.sale_line_id
                    for invoice_line in line.invoice_lines:
                        # si la linea no tiene comisiones se arrastran los del
                        # pedido a la linea de factura
                        if not line.line_agent_ids:
                            for so_comm in line.order_id.sale_agent_ids:
                                line_agent_id = self._create_invoice_line_agent(
                                    cr, uid, [], so_comm.agent_id.id,
                                    so_comm.commission_id.id, invoice_line.id)
                        else:
                            for l_comm in line.line_agent_ids:
                                line_agent_id = self._create_invoice_line_agent(
                                    cr, uid, [],
                                    l_comm.agent_id.id,
                                    l_comm.commission_id.id, invoice_line.id)

        return invoices
