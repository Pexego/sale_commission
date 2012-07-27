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

"""View that filter stock_moves by not state = 'cancel' Use this view to show traceability tree"""

from osv import osv, fields
from tools.translate import _
from tools.sql import drop_view_if_exists

class report_partner_affected_bycase(osv.osv):
    """View with partner affected by blockade case"""
    _name = "report.partner.affected.bycase"
    _auto = False

    _columns = {
            'id': fields.integer('Id', readonly=True),
            'prodlot_id': fields.many2one('stock.production.lot', 'Production Lot', readonly=True, select=True),
            'product_id': fields.many2one('product.product', 'Product', readonly=True, select=True),
            'product_qty': fields.float('Quantity', readonly=True),
            'case_id': fields.many2one('block.prodlot.cases', 'Blockade Case', readonly=True, select=True),
            'picking_id': fields.many2one('stock.picking', 'Picking', readonly=True, select=True),
            'sale_line_id': fields.many2one('sale.order.line', 'Sale Order Line', select=2, readonly=True),
            'address_id': fields.many2one('res.partner.address', 'Address', readonly=True, select=2),
            'partner_id': fields.many2one('res.partner', 'Costumer', readonly=True, select=True),
            'vat': fields.char('Vat', size=12, readonly=True),
            'fax': fields.char('Fax', size=12, readonly=True),
            'city': fields.char('City', size=32, readonly=True),
            'phone': fields.char('Phone', size=12, readonly=True),
            'zip': fields.char('Zip', size=7, readonly=True),
            'country_id': fields.many2one('res.country', 'Country', readonly=True, select=2),
            'email': fields.char('Email', size=32, readonly=True),
            'date': fields.datetime('Date', readonly=True),
    }

    def init(self, cr):
        """creates view when install"""
        drop_view_if_exists(cr, 'report_partner_affected_bycase')

        cr.execute("""
            create or replace view report_partner_affected_bycase as (
                select stock_move.id as id, prodlots.id as prodlot_id, prodlots.case_id, stock_move.picking_id, stock_move.date,
                stock_move.sale_line_id, addresses.id as address_id, res_partner.id as partner_id,
                res_partner.vat, addresses.fax, addresses.city, addresses.phone,
                addresses.zip, addresses.country_id, addresses.email, prodlots.product_id as product_id,
                stock_move.product_qty
                from stock_move inner join
                (select distinct stock_production_lot.*, case_id from stock_production_lot inner join
                blocked_prodlots_cases_ids on id = blocked_prodlot) as prodlots
                on stock_move.prodlot_id = prodlots.id inner join
                stock_location on stock_move.location_dest_id = stock_location.id inner join
                res_partner on res_partner.id = stock_location.partner_id left join
                (select * from res_partner_address limit 1) as addresses on addresses.partner_id = res_partner.id)""")

    def unlink(self, cr, uid, ids, context={}):
        """not can delete, beacause is database view"""
        raise osv.except_osv(_('Error !'), _('You cannot delete any record!'))


report_partner_affected_bycase()