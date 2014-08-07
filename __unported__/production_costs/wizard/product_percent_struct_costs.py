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

"""
    Auxiliary object to mate products with structural costs
"""

from osv import osv, fields
import time
import decimal_precision as dp
import calendar
from tools.translate import _

class product_percent_struct_costs(osv.osv_memory):
    """
        Auxiliar object to associate percentually costs to products
    """
    def onchange_product_id(self, cr, uid, ids, prev_fyear_id, prev_period_id, product_id):
        """
            Gets total sales for this product, fiscal year and period
        """
        res ={}
        total_sales = 0.0
        sales_facade = self.pool.get('sale.order')
        fiscalyear = self.pool.get('account.fiscalyear').browse(cr, uid, prev_fyear_id)
        if not prev_period_id:
            from_date =fiscalyear.date_start
            to_date = fiscalyear.date_stop
        else:
            period = self.pool.get('account.period').browse(cr, uid, prev_period_id)
            from_date = period.date_start
            to_date = period.date_stop

        period_sales = sales_facade.browse(cr, uid, sales_facade.search(cr, uid, [('state','not in',['draft','cancel']),('date_order','<=', to_date), ('date_order','>=', from_date)]))
        for sale in period_sales:
            for line in sale.order_line:
                if line.product_id:
                    if line.product_id.id == product_id:
                        total_sales += line.product_uom_qty

        res['total_sales'] = total_sales
        res['forecasted_sales'] = total_sales

        return {'value': res}


    def onchange_total_sales(self, cr, uid, ids, total_sales):
        """
            Refresh forecasted values according total sales
        """
        res ={}
        if total_sales:
            res['forecasted_sales'] = total_sales
        else:
            res['forecasted_sales'] = 0.0
        return {'value': res}


    _name = 'product.percent.struct.costs'
    _description = 'Structural products cost'
    _columns = {
        'product_id': fields.many2one('product.product','Product',required=True),
        'total_sales': fields.float('Sold Units', digits_compute=dp.get_precision('Account'), required=True),
        'forecasted_sales': fields.float('Forecasted Sold Units', digits_compute=dp.get_precision('Account')),
        'wizard_id': fields.many2one('structural.costs.impact.wizard','Wizard'),
    }

    _defaults = {
        'wizard_id': lambda self, cr, uid, context: context.get('parent_id') and context['parent_id'] or False,
    }


product_percent_struct_costs()