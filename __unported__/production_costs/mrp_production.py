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

from osv import fields, osv
from tools.translate import _
import decimal_precision as dp
import time
from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule

class mrp_production(osv.osv):


    def onchange_production_dates(self, cr, uid, ids, begin_production_date, end_production_date, production_duration, context=None):
        """
            Returns duration and/or end date based on values passed
        """
        if context is None:
            context = {}
        value = {}
        if not begin_production_date:
            return value
        if not end_production_date and not production_duration:
            duration = 1.00
            value[production_duration] = duration

        start = datetime.strptime(begin_production_date, "%Y-%m-%d %H:%M:%S")
        if end_production_date and not production_duration:
            end = datetime.strptime(end_production_date, "%Y-%m-%d %H:%M:%S")
            diff = end - start
            duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
            value[production_duration] = round(duration, 2)
        elif not end_production_date:
            end = start + timedelta(hours=production_duration)
            value[end_production_date] = end.strftime("%Y-%m-%d %H:%M:%S")
        elif end_production_date and production_duration:
            # we have both, keep them synchronized:
            # set duration based on end_date (arbitrary decision: this avoid
            # getting dates like 06:31:48 instead of 06:32:00)
            end = datetime.strptime(end_production_date, "%Y-%m-%d %H:%M:%S")
            diff = end - start
            duration = float(diff.days)* 24 + (float(diff.seconds) / 3600)
            value['production_duration'] = round(duration, 2)

        return {'value': value}

    _inherit = 'mrp.production'
    _columns = {
        'begin_production_date': fields.datetime('Begin production date', required=True),
        'end_production_date': fields.datetime('End production date', required=True),
        'production_duration': fields.float('Duration', digits_compute=dp.get_precision('Account')),
        'production_manpower': fields.one2many('mrp.production.manpower', 'production_id', 'Production manpower', required=True),
        'products_total_cost': fields.float('Material total cost', digits_compute=dp.get_precision('Account'), readonly=True),
        #'unit_product_cost': fields.float('Material unit cost', digits_compute=dp.get_precision('Account'), readonly=True),
        'manpower_cost': fields.float('Manpower total cost', digits_compute=dp.get_precision('Account'), readonly=True),
        #'manpower_unit_cost': fields.float('Manpower unit cost', digits_compute=dp.get_precision('Account'), readonly=True),
        'total_production_cost': fields.float('Total production cost', digits_compute=dp.get_precision('Account'), readonly=True),
        #'unit_production_cost': fields.float('Unit production cost', digits_compute=dp.get_precision('Account'), readonly=True),
        'total_fixed_cost': fields.float('Total fixed cost', digits_compute=dp.get_precision('Account'), readonly=True),
        #'unit_fixed_cost': fields.float('Unit fixed cost', digits_compute=dp.get_precision('Account'), readonly=True),
        #'new_standard_price': fields.float('New standard product price', digits_compute=dp.get_precision('Account'), readonly=True, help="New product price (only if its cost method is set to average)"),
        'unit_costs': fields.one2many ('mrp.production.unit.costs', 'production_id', 'Unit costs by product')
    }
    _defaults = {
        'begin_production_date': lambda *a: time.strftime('%Y-%m-%d 08:00:00'),
        'end_production_date': lambda *a: time.strftime('%Y-%m-%d 13:00:00'),
        'production_duration': 5.0
    }

    def action_compute_price(self, cr, uid, ids, context=None):
        """compute final lot price"""
        if context is None: context = {}
        production_obj_id = self.browse(cr, uid, ids[0])
        final_product_id = production_obj_id.product_id.id

        for final_move_obj_id in (production_obj_id.move_created_ids2 or production_obj_id.move_created_ids):
            if final_move_obj_id.state != 'cancel':
                if final_move_obj_id.product_id.id == final_product_id and not final_move_obj_id.prodlot_id and final_move_obj_id.state != 'cancel':
                    raise osv.except_osv(_('Warning!'), _('Must assign first production lot in principal final move with product: %s') % final_move_obj_id.product_id.name)
                elif final_move_obj_id.product_id.id == final_product_id:
                    total_price = 0.0
                    
                    for move_line in production_obj_id.move_lines2:
                        if move_line.state != 'cancel':
                            total_price += move_line.price

                    if production_obj_id.unit_costs:
                        for line_unit_costs in production_obj_id.unit_costs:
                            total_price += line_unit_costs.manpower_unit_cost

                    unit_price = total_price / final_move_obj_id.product_qty
                    self.pool.get('stock.production.lot').write(cr, uid, [final_move_obj_id.prodlot_id.id], {'unit_price': unit_price})
                    break
        return True

mrp_production()

class mrp_production_unit_costs (osv.osv):
    _name = 'mrp.production.unit.costs'
    _description = 'Production unit Costs'
    
    _columns = {
        'production_id': fields.many2one('mrp.production', 'Production', required=True),
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'unit_product_cost': fields.float('Material unit cost', digits_compute=dp.get_precision('Production costs'), readonly=True),
        'manpower_unit_cost': fields.float('Manpower unit cost', digits_compute=dp.get_precision('Production costs'), readonly=True),
        'unit_production_cost': fields.float('Unit production cost', digits_compute=dp.get_precision('Production costs'), readonly=True),
        'unit_fixed_cost': fields.float('Unit fixed cost', digits_compute=dp.get_precision('Production costs'), readonly=True),
        'new_standard_price': fields.float('New standard product price', digits_compute=dp.get_precision('Production costs'), readonly=True, help="New product price (only if its cost method is set to average)"),
        'date': fields.related('production_id', 'date_finished', type='datetime', string='DAte', store=True, readonly=True),
    }
    
mrp_production_unit_costs()

class mrp_product_produce(osv.osv_memory):

    _inherit = 'mrp.product.produce'


    def do_produce(self, cr, uid, ids, context=None):
        """
        Inherits method for setting all new products and manpower costs for production
        """
        #Calculating manpower total and unitary cost

        if context.get('active_ids') and context['active_ids']:
            for production in self.pool.get('mrp.production').browse(cr, uid, context['active_ids']):
                manpower_cost = 0.0
                sum_products_cost = 0.0
                sum_fixed_cost = 0.0
                qty_finished_products = 0.0
                qty_consumed_products = 0.0

                #First of all, identify the main production product between all finished products
                main_product = False
                finished_products = production.move_created_ids  
                for fin_prod in finished_products:
                    qty_finished_products +=fin_prod.product_qty
                    if fin_prod.product_id.id == production.product_id.id:
                        main_product = fin_prod

                if not main_product:
                    main_product = production
                #Gets product stock before producing...
                
                result = super(mrp_product_produce, self).do_produce(cr, uid, ids, context)

                #Manpower cost
                number_of_workers = len(production.production_manpower)
                if not number_of_workers > 0:
                    raise osv.except_osv(_('Warning!'), _('There are no assigned workers to this production. Please, specify some before continuing...'))
                for worker in production.production_manpower:
                    if not worker.employee_id.product_id:
                        raise osv.except_osv(_('Warning!'), _('This worker does not have associated an "hour" product. Please, set it before continuing...'))
                    manpower_cost += worker.employee_id.product_id.standard_price * worker.production_duration
                tot_production_manpower_cost = manpower_cost
                unit_manpower_cost = tot_production_manpower_cost / production.product_qty
                
                qty_finished_products = 0 
                for fin_prod in production.move_created_ids2:
                    if fin_prod.product_id.id == production.product_id.id:
                        qty_finished_products +=fin_prod.product_qty
                if not qty_finished_products > 0:
                    raise osv.except_osv(_('Error!'), _('No existen productos finalizados en la orden de producción'))
                
                #Material cost ((list price consumed products * qty)/sum_qty)
                for consumed_product in production.move_lines2:
                    sum_products_cost += consumed_product.product_id.standard_price * consumed_product.product_qty
                    qty_consumed_products += consumed_product.product_qty
                tot_products_cost = sum_products_cost
                #if not qty_finished_products: qty_finished_products = qty_consumed_products
                unit_product_cost = tot_products_cost / qty_finished_products

                #Fixed costs (sum of all fixed costs)
                for fixed_cost in production.fixed_costs:
                    sum_fixed_cost += fixed_cost.amount
                    
                unit_fixed_cost = sum_fixed_cost / qty_finished_products


                stock_before_producing = main_product.product_id.qty_available - qty_finished_products
                #Total cost (Manpower cost + material cost + fixed cost + structural cost)
                total_production_cost = tot_production_manpower_cost + tot_products_cost + sum_fixed_cost
                #unit_production_cost = (total_production_cost / qty_finished_products) + main_product.product_id.structural_cost + unit_fixed_cost
                
                unit_production_cost = (total_production_cost / qty_finished_products) + unit_fixed_cost + unit_manpower_cost
                
                #New product standard price (PMP) = ((product stock before producing * standard price) + (unit_production_cost * prod_qty)) / (stock before producing + produced_qty)
                new_product_standard_price = ((stock_before_producing * main_product.product_id.standard_price) + (unit_production_cost * qty_finished_products))/ (stock_before_producing + qty_finished_products)

                #Updates cost management fields for this production
                vals_production = {
                    'products_total_cost': tot_products_cost,
                    #'unit_product_cost': unit_product_cost,
                    'manpower_cost': tot_production_manpower_cost,
                    #'manpower_unit_cost': unit_manpower_cost,
                    'total_fixed_cost': sum_fixed_cost,
                    #'unit_fixed_cost': unit_fixed_cost,
                    'total_production_cost': total_production_cost,
                    #'unit_production_cost': unit_production_cost,
                    #'new_standard_price': new_product_standard_price
                }
                self.pool.get('mrp.production').write(cr, uid, [production.id], vals_production)

                # Create line for the unit production
                vals_unit_costs = {
                    'production_id': production.id,
                    'product_id': main_product.product_id.id,
                    'unit_product_cost': unit_product_cost,
                    'manpower_unit_cost': unit_manpower_cost,
                    'unit_fixed_cost': unit_fixed_cost,
                    'unit_production_cost': unit_production_cost,
                    'new_standard_price': new_product_standard_price
                }
                
                self.pool.get('mrp.production.unit.costs').create(cr, uid, vals_unit_costs)
                
                
                #Finally we update product list_price and manpower fields accordingly
                # This is por compatibilty with new modules that must write tehe costs later
                
                # It depends of context if it musts write de average price in the product
                if not (context.get('skip_write') and context['skip_write']):
                   
                    vals_product = {}
                    if main_product.product_id.cost_method == 'average':
                        vals_product['standard_price'] = new_product_standard_price
                        
                    # Cálculo de los precios medios para actualziar ficha de producto
                    
                    pm_manpower_cost = ((stock_before_producing * main_product.product_id.manpower_cost) + (unit_manpower_cost * qty_finished_products))/ (stock_before_producing + qty_finished_products)
                    pm_fixed_cost = ((stock_before_producing * main_product.product_id.other_prod_cost) + (unit_fixed_cost * qty_finished_products))/ (stock_before_producing + qty_finished_products)
                    pm_product_cost = ((stock_before_producing * main_product.product_id.other_prod_cost) + (unit_product_cost * qty_finished_products))/ (stock_before_producing + qty_finished_products)

                    vals_product['manpower_cost'] = pm_manpower_cost
                    vals_product['other_prod_cost'] = pm_fixed_cost
                    vals_product['product_cost'] = pm_product_cost

                    self.pool.get('product.product').write(cr, uid, main_product.product_id.id, vals_product)

                return result
                

mrp_product_produce()
