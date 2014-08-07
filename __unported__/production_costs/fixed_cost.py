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

class mrp_production_fixed_costs(osv.osv):
    """
        Class that represents a production fixed costs
    """
    _name = 'mrp.production.fixed.costs'
    _columns = {
        'name': fields.char('Description', size=128, required=True),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'production_id': fields.many2one('mrp.production', 'Production', required=True),
        'company_id': fields.many2one('res.company', 'Company')
    }

    _defaults = {
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.id,
        'production_id': lambda self, cr, uid, context: context.get('parent_id') and context['parent_id'] or False,
    }

mrp_production_fixed_costs()

class mrp_production_add_fixed_costs(osv.osv):

    _inherit = 'mrp.production'
    _columns = {
        'fixed_costs': fields.one2many('mrp.production.fixed.costs', 'production_id', 'Production fixed costs'),
    }

mrp_production_add_fixed_costs()