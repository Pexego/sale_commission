# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved.
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
        "name" : "Production Costs Management Module",
        "version" : "1.0",
        "author" : "Pexego",
        "website" : "http://www.pexego.es",
        "category" : "Production",
        "description": """
                Production Costs Management Module. Includes:
                -Extension of production order to calculate manpower, material and fixed costs.
                -Extension of products for adding these three prior fields and updating its cost price (only if its 'cost_method' field is set to 'average').
                -A new wizard for repercuting structural costs over products.

                -Obtains prices of final production product. Prices in moves. Unit price in production lot, taking into account the cost of manpower.
                """,
        "depends" : [
            'base',
            'mrp',
            'analytic',
            'product',
            'hr_timesheet',
            'stock'
            ],
        "init_xml" : [],
        "demo_xml" : [],
        "update_xml" : [
                'security/ir.model.access.csv',
		'product_cost_data.xml',
                'product_product_view.xml',
                'mrp_production_view.xml',
                'production_manpower_view.xml',
                'fixed_cost_view.xml',
                'wizard/structural_costs_impact_wizard_view.xml',
                'wizard/product_percent_struct_costs_view.xml',
                'stock_move_view.xml',
                'stock_production_lot_view.xml',
                'unit_costs.xml'
            ],
        "installable": True,
        'active': False

}
