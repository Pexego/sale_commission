# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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

class mrp_bom(osv.osv):
    _inherit = "mrp.bom"
    _columns = {
         'employees_ids': fields.many2many('hr.employee', 'employee_mrp_rel', 'bom_id','employee_id', 'Employees')
    }
    
mrp_bom()

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    def explode_employees(self,cr,uid,ids,context=None):
        if context is None: context = {}
        employees = []
        for production in self.browse(cr,uid,ids):
            if production.bom_id.employees_ids:
                for employees_id in production.bom_id.employees_ids:
                    employees.append({
                        'employee_id': employees_id.id
                    })
        return employees
    def action_compute(self,cr,uid,ids,properties=[],context=None):
        if context is None: context = {}
        results = super(mrp_production, self).action_compute(cr, uid, ids, properties,context=context)
        empl = []
        production_obj = self.pool.get('mrp.production')
        bom_obj = self.pool.get('mrp.bom')
        man_power_obj = self.pool.get('mrp.production.manpower')
        for production in self.browse(cr,uid,ids):
            employees = production_obj.explode_employees(cr,uid,ids)
            for line in employees:
                line['production_id'] = production.id
                man_power_obj.create(cr, uid, line)
           
        return results


mrp_production()

     
            
           