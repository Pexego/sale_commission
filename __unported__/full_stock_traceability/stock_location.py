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

from osv import osv, fields

def intersect(visible_lots, lots):
    """returns only visible lots in the list"""
    return filter(lambda x: x in visible_lots, lots)

class stock_location(osv.osv):

    _inherit = "stock.location"

    def get_lots_inside(self, cr, uid, location_id, product_id, context=None):
        """return lots in location
            @return: list of lots"""
        if context is None: context = {}

        cr.execute('''select
                prodlot_id
            from
                stock_report_prodlots
            where
                location_id = %s and product_id = %s and qty > 0''', (location_id, product_id))

        prodlot_ids = cr.fetchall()
        all_visible_prodlots = self.pool.get('stock.production.lot').search(cr, uid, [], context=context)

        if prodlot_ids:
            return intersect(all_visible_prodlots, [x[0] and int(x[0]) for x in prodlot_ids])
        else:
            return []

    _columns = {
                'usage': fields.selection([('supplier', 'Supplier Location'), ('view', 'View'), ('internal', 'Internal Location'), ('customer', 'Customer Location'), ('inventory', 'Inventory'), ('procurement', 'Procurement'), ('production', 'Production'), ('transit', 'Transit Location for Inter-Companies Transfers'), ('intermediate','Intermediate')], 'Location Type', required=True,
                 help="""* Supplier Location: Virtual location representing the source location for products coming from your suppliers
                       \n* View: Virtual location used to create a hierarchical structures for your warehouse, aggregating its child locations ; can't directly contain products
                       \n* Internal Location: Physical locations inside your own warehouses,
                       \n* Customer Location: Virtual location representing the destination location for products sent to your customers
                       \n* Inventory: Virtual location serving as counterpart for inventory operations used to correct stock levels (Physical inventories)
                       \n* Procurement: Virtual location serving as temporary counterpart for procurement operations when the source (supplier or production) is not known yet. This location should be empty when the procurement scheduler has finished running.
                       \n* Production: Virtual counterpart location for production operations: this location consumes the raw material and produces finished products
                       \n* Intermediate: Virtual counterpart location for mix operations: this location consumes goods to mix and produces mixed goods
                      """, select = True),
                'miscible_location': fields.boolean('Mixtures Location',help="If the location is only for miscible products, check it, this check obligate to have inside a product always with product lot."),
                }

    _defaults = {
                 'miscible_location': lambda *a: 0,
                 }

stock_location()
