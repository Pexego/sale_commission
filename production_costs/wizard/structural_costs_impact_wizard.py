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
    Wizard to impact structural costs over products
"""

from osv import osv, fields
import time
import decimal_precision as dp
import calendar
from tools.translate import _

COST_METHODS = [
    ('novalid','Please, select a method for impacting costs...'),
    ('uniform','Uniform'),
]


class structural_costs_impact_wizard(osv.osv_memory):
    """
    Wizard to percentually impact structural costs on service products
    """

    def onchange_analytic_account(self, cr, uid, ids, fiscalyear_id, period_id, account_id):
        """
            Gets total amount from chosen analytical account and year
        """
        res ={}
        context = {}
        res['structural_cost'] = 0.0
        struct_cost_facade = self.pool.get('product.percent.struct.costs')
        sales_facade = self.pool.get('sale.order')
        if account_id:
            fiscalyear = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyear_id)
            if not period_id:
                context['from_date'] =fiscalyear.date_start
                context['to_date'] = fiscalyear.date_stop
            else:
                period = self.pool.get('account.period').browse(cr, uid, period_id)
                context['from_date'] = period.date_start
                context['to_date'] = period.date_stop
            account = self.pool.get('account.analytic.account').browse(cr, uid, account_id, context)
            res['structural_cost'] = account.credit

            #Forces creation of product lines based on sales made on chosen period and fiscal year...
            period_sales = sales_facade.browse(cr, uid, sales_facade.search(cr, uid, [('state','not in',['draft','cancel']),('date_order','<=', context['to_date']), ('date_order','>=', context['from_date'])]))
            distinct_sale_products = {}
            product_line_ids = []
            for sale in period_sales:
                for line in sale.order_line:
                    if line.product_id:
                        if line.product_id.id not in distinct_sale_products.keys():
                            distinct_sale_products[line.product_id.id] = line.product_uom_qty
                        else:
                            distinct_sale_products[line.product_id.id] += line.product_uom_qty
                            
            for product_id in distinct_sale_products.keys():
                vals_product_line = {
                    'product_id': product_id,
                    'total_sales': distinct_sale_products[product_id],
                    'forecasted_sales': distinct_sale_products[product_id],
                    #'wizard_id': self.next_id + 1
                }
                #line_id = struct_cost_facade.create(cr, uid, vals_product_line)
                product_line_ids.append(vals_product_line)

            res['products_percent'] = product_line_ids

        return {'value': res}

    def onchange_cost_method(self, cr, uid, ids, cost_method, structural_cost, products_percent):
        """
            Gets amount to impact over chosen products based on sales forecast
        """
        res ={}
        res['cost_to_impact'] = 0.0
        sum_forecasted_sales = 0.0
        if cost_method == 'uniform':
            for product_line in products_percent:
                sum_forecasted_sales += product_line[2]['forecasted_sales']
            res['cost_to_impact'] = structural_cost / sum_forecasted_sales
        return {'value': res}


    def _get_current_user_company(self, cr, uid, context={}):
        """
            Obtiene la compañía del usuario activo
        """
        current_user = self.pool.get('res.users').browse(cr,uid,uid)
        return current_user.company_id.id

    def _get_previous_fiscalyear(self, cr, uid, context):
        """
            Get previous current year
        """
        fyear_facade = self.pool.get('account.fiscalyear')
        current_fyear = context and context.get('fiscalyear_id', None) or fyear_facade.browse(cr, uid, uid)
        try:
            prev_date_start = '%s-01-01' %(str(int(current_fyear.date_start[0:4])-1))
        except Exception:
            raise osv.except_osv(_('Error!'), _('Are fiscal years already defined...?'))
        prev_date_end = '%s-12-31' %(str(int(current_fyear.date_start[0:4])-1))
        prev_fyear = fyear_facade.search(cr, uid, [('company_id','=',current_fyear.company_id.id), ('date_start','>=',prev_date_start),('date_stop','<=',prev_date_end)])
        prev_fyear = prev_fyear and prev_fyear[0] or None
        if not prev_fyear:
            return current_fyear.id
        else:
            return prev_fyear

    def action_impact_struct_costs(self, cr, uid, ids, *args):
        """
            Simply opens a list view of all modified products
        """
        modified_prod_ids = []
        view_facade = self.pool.get('ir.ui.view')
        product_facade = self.pool.get('product.product')
        for wizard in self.browse(cr, uid, ids):
            for line in wizard.products_percent:
                product_facade.write(cr, uid, line.product_id.id, {'structural_cost': wizard.cost_to_impact})
                modified_prod_ids.append(line.product_id.id)

            product_list_view_id = view_facade.search(cr, uid, [('name', '=', 'view.add.costs.product.view.list')])[0]
            product_form_view_id = view_facade.search(cr, uid, [('name', '=', 'view.add.costs.product.view.form')])[0]

            #Finalmente, devolvemos la vista correspondiente...
            return {
                'name' : _('Impacted Products'),
                'type' : 'ir.actions.act_window',
                'res_model' : 'product.product',
                'view_type' : 'form',
                'view_mode' : 'tree,form',
                'domain' : "[('id', 'in', %s)]" % modified_prod_ids,
                'view_id' : False,
                'views': [(product_list_view_id, 'tree'), (product_form_view_id, 'form'), (False, 'calendar'), (False, 'graph')],
            }


    _name = 'structural.costs.impact.wizard'
    _description = "Structural costs impact Wizard"

    _columns = {
        'prev_fyear_id' : fields.many2one('account.fiscalyear', 'Fiscal Year to Look', required=True),
        'prev_period_id' : fields.many2one('account.period', 'Period'),
        'struct_analytic_acc_id': fields.many2one('account.analytic.account','Structural Expenses Analytic Account'),
        'structural_cost': fields.float('Structural Costs', digits_compute=dp.get_precision('Account')),
        'products_percent': fields.one2many('product.percent.struct.costs', 'wizard_id', 'Sold Products during chosen fiscal year and/or period'),
        'structural_cost_method': fields.selection(COST_METHODS, 'Cost Method',required=True, help='Uniform method: all costs are distributed equally amongst products.'),
        'cost_to_impact': fields.float('Cost over products', digits_compute=dp.get_precision('Account'), help='Cost based on forecasted sales.'),
        'company_id': fields.many2one('res.company', 'Company')
    }
    _defaults = {
        #'prev_fyear_id': _get_previous_fiscalyear,
        'company_id': lambda self, cr, uid, context: self._get_current_user_company(cr, uid, context),
        'structural_cost_method': lambda *a: 'novalid'
    }

structural_costs_impact_wizard()