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


{
    "name" : "Stock Block Production Lots",
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ["base","product","stock","full_stock_traceability","product_expiry","sale_follow_up","sale"],
    "category" : "My Modules/Inventory Control",
    "init_xml" : [],
    "update_xml" : ['security/ir.model.access.csv',
                    'stock_block_prodlots_wizard.xml',
                    'stock_data.xml',
                    'product_view.xml',
                    'stock_production_lot_view.xml',
                    'block_prodlot_case_view.xml',
                    'report_partners_affected_view.xml',
                    'security/groups.xml',
                    'wizard/add_prodlots_to_case_wzd_view.xml',
                    'wizard/block_prodlots_wzd_view.xml',
                    'stock_picking_view.xml',
                    'partner_view.xml'],
    'demo_xml': [],
    "website": 'http://www.pexego.es',
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
