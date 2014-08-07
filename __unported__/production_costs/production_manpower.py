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

from osv import osv, fields
from tools.translate import _
import decimal_precision as dp
import time
from datetime import datetime, timedelta, date
from dateutil import parser
from dateutil import rrule

class mrp_production_manpower(osv.osv):

    def onchange_dates(self, cr, uid, ids, start_date, end_date, production_duration, context=None):
        """
            Updates duration according start and end dates...
        """
        production_facade = self.pool.get('mrp.production')
        duration_as_dict = production_facade.onchange_production_dates(cr, uid, ids, start_date, end_date, production_duration)
        return duration_as_dict


    def onchange_employee(self, cr, uid, ids, employee_id, context=None):
        """
            Checks if chosen employee has an associated product...
        """
        if employee_id:
            chosen_employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            if not chosen_employee.product_id:
                raise osv.except_osv(_('Warning!'), _('There is no product defined for this employee. Please, define one before continuing...'))
            
        return employee_id


    _name = 'mrp.production.manpower'
    _rec_name = 'employee_id'
    _description = 'Production manpower involved'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'start_date': fields.datetime('Start date'),
        'end_date': fields.datetime('End date'),
        'production_duration': fields.float('Duration', digits_compute=dp.get_precision('Account'), required=True),
        'company_id': fields.many2one('res.company','Company'),
        'production_id': fields.many2one('mrp.production', 'Related production order')
    }

    _defaults = {
        'start_date': lambda *a: time.strftime('%Y-%m-%d 08:00:00'),
        'end_date': lambda *a: time.strftime('%Y-%m-%d 13:00:00'),
        'production_duration': 5.0,
        'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid).company_id.id
    }

mrp_production_manpower()