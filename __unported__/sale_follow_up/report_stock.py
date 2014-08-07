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

"""inherits from stock_report_prodlots adds a column to view, add partner_id because now there are partner_locations or sale locations"""

from osv import osv, fields
from tools.translate import _
from tools.sql import drop_view_if_exists

#
# Check if it works with UoM ???
#
class stock_report_prodlots(osv.osv):
    """inherits from stock_report_prodlots adds a columsn to view, add partner_id because now there are partner_locations or sale locations"""
    _inherit = "stock.report.prodlots"
    _auto = False
    _rec_name = 'qty'
    
    _columns = {
            'qty': fields.float('Quantity', readonly=True),
            'location_id': fields.many2one('stock.location', 'Location', readonly=True, select=True),
            'product_id': fields.many2one('product.product', 'Product', readonly=True, select=True),
            'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', readonly=True, select=True),
            'partner_id': fields.many2one('res.partner','Customer', readonly=True, select=True),
    }
    
    def init(self, cr):
        """overwrites the create query"""
        drop_view_if_exists(cr, 'stock_report_prodlots')

        cr.execute("""
            create or replace view stock_report_prodlots as (
                select max(id) as id,
                    location_id,
                    product_id,
                    prodlot_id,
                    partner_id,
                    sum(qty) as qty
                from (
                    select -max(sm.id) as id,
                        sm.location_id,
                        sm.product_id,
                        sm.prodlot_id,
                        sl.partner_id,
                        -sum(sm.product_qty /uo.factor) as qty
                    from stock_move as sm
                    left join stock_location sl
                        on (sl.id = sm.location_id)
                    left join product_uom uo
                        on (uo.id=sm.product_uom)
                    where state = 'done'
                    group by sm.location_id, sm.product_id, sm.product_uom, sm.prodlot_id, sl.partner_id
                    union all
                    select max(sm.id) as id,
                        sm.location_dest_id as location_id,
                        sm.product_id,
                        sm.prodlot_id,
                        sl.partner_id,
                        sum(sm.product_qty /uo.factor) as qty
                    from stock_move as sm
                    left join stock_location sl
                        on (sl.id = sm.location_dest_id)
                    left join product_uom uo
                        on (uo.id=sm.product_uom)
                    where sm.state = 'done'
                    group by sm.location_dest_id, sm.product_id, sm.product_uom, sm.prodlot_id, sl.partner_id
                ) as report
                group by location_id, product_id, prodlot_id, partner_id
            )""")
        
    def unlink(self, cr, uid, ids, context={}):
        """not allow delete any record, is a database view"""
        raise osv.except_osv(_('Error !'), _('You cannot delete any record!'))

        
stock_report_prodlots()
