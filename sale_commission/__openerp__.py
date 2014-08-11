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
{
    'name' : 'Sales commissions',
    'version': '1.0',
    'author' : 'Pexego',
    "category": "Generic Modules/Sales & Purchases",
    'depends' : [
                    'base',
                    'account',
                    'product',
                    'sale',
                    'sale_stock',
                    'hr',
                    'stock'
                ],
    'description': 'Sales commissions',
    'data': [
                'security/ir.model.access.csv',
                'saleagent_view.xml',
                'partner_agent_view.xml',
                'wizard/wizard_invoice.xml',
                'partner_view.xml',
                'settled_view.xml',
                'invoice_view.xml',
                'sale_order_view.xml',
                'product_view.xml',
                'stock_picking_view.xml',
                'cc_commission_report.xml',
            ],
    'installable': True,
    'application': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

