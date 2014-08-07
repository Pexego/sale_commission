# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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

import osv
import pooler
import addons
from lxml import etree

if 'old_fields_view_get' not in dir(osv.orm.BaseModel):
    osv.orm.BaseModel.old_fields_view_get = osv.orm.BaseModel.fields_view_get
if 'old_create' not in dir(osv.orm.BaseModel):
    osv.orm.BaseModel.old_create = osv.orm.BaseModel.create
if 'old_write' not in dir(osv.orm.BaseModel):
    osv.orm.BaseModel.old_write = osv.orm.BaseModel.write

def fields_view_get(self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
    if context is None: context = {}
    
    def _check_rec(eview, value, str_to_add):
        """busca recursivamente en el arch del xml el atributo domain con un valor dado y lo substituye por un nuevo valor"""
        if eview.attrib.get('name', False) == value:
            eview.addnext(etree.fromstring(str_to_add))
        for child in eview:
            res = _check_rec(child, value, str_to_add)
        return False
    
    res = self.old_fields_view_get(cr, user, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
    
    if view_type == 'form':
        found = self.pool.get('ir.model.data').search(cr, user, [('model', '=', self._name)], limit=1)
        if found:
            field = False
            if 'name' in self._columns:
                field = 'name'
            else:
                field = self._rec_name
                
            eview = etree.fromstring(res['arch'])
            line = _check_rec(eview, field, "<field name='x_noupdate'/>\n")
            res['arch'] = etree.tostring(eview)
            res['fields'].update(self.fields_get(cr, user, 'x_noupdate', context))
                
    return res
    
def create_noupdate_field(cr, user, model, pool=False):
    if not pool:
        pool = pooler.get_pool(cr.dbname)
    model_ids = pool.get('ir.model').search(cr, user, [('model','=',model)])
    field_found = pool.get('ir.model.fields').search(cr, user, [('name', '=', 'x_noupdate'),('model_id','=',model_ids[0])])
    if not field_found:
        field_vals = {
            'field_description': 'No update',
            'model_id': model_ids[0],
            'model': model,
            'name': 'x_noupdate',
            'ttype': 'boolean',
            'required': False,
            'state': 'manual'
        }
        pool.get('ir.model.fields').create(cr, user, field_vals)
    
def create(self, cr, user, vals, context=None):
    if context is None: context = {}
    
    res = self.old_create(cr, user, vals, context=context)
    if self._name == 'ir.model.data':
        obj = self.pool.get(vals['model'])
        if 'x_noupdate' not in obj._columns:
            create_noupdate_field(cr, user, self._name, self.pool)
            
        if vals.get('noupdate', False):
            self.pool.get(obj._name).old_write(cr, user, {'x_noupdate': vals.get('noupdate', False)})
        
    return res
    
def write(self, cr, user, ids, vals, context=None):
    if context is None: context = {}
    if isinstance(ids, (int,long)):
        ids = [ids]
    
    res = self.old_write(cr, user, ids, vals, context=context)
    
    model_found = self.pool.get('ir.model.data').search(cr, user, [('model','=',self._name)], limit=1)
    if model_found:
        if 'x_noupdate' not in self._columns:
            create_noupdate_field(cr, user, self._name, self.pool)
        else:
            for id in ids:
                if 'x_noupdate' in vals:
                    id_found = self.pool.get('ir.model.data').search(cr, user, [('model','=',self._name),('res_id','=',id)], limit=1)
                    self.pool.get('ir.model.data').old_write(cr, user, id_found, {'noupdate': vals['x_noupdate']})
            
    return res  
    
    
osv.orm.BaseModel.fields_view_get = fields_view_get
osv.orm.BaseModel.create = create
osv.orm.BaseModel.write = write
