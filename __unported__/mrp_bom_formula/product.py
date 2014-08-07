# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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

class product_product(osv.osv):
    _inherit = "product.product"

    _columns = {
        'product_fields_ids': fields.many2many('product.fields', 'product_product_fields_rel', 'product_id', 'product_field_id', 'Products Fields'),
    }

product_product()

class product_fields(osv.osv):
    _name = "product.fields"
    _description = "Add fields to stock.production.lot"
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'field_description': fields.char('Field Label', size=64, required=True, translate=True),
        'translate':fields.boolean('Translate'),
        'required':fields.boolean('Required'),
        'product_id': fields.many2many('product.product', 'product_product_fields_rel', 'product_field_id','product_id', 'Products'),
        'sequence': fields.char('Sequence', size=3, select=1, readonly=True),
        'field_id': fields.many2one('ir.model.fields', 'product_id'),
    }
    _defaults = {
        'name':lambda * a:'x_',
    }

    def create(self, cr, uid, vals, context=None):
        model_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'stock.production.lot')])[0]

        field_vals = {
            'field_description': vals['field_description'],
            'model_id': model_id,
            'model': 'stock.production.lot',
            'name':vals['name'],
            'ttype': 'float',
            'translate': vals['translate'],
            'required': vals['required'],
            'state': 'manual',

        }

        vals['field_id'] = self.pool.get('ir.model.fields').create(cr, uid, field_vals)

        sequence = self.pool.get('ir.sequence').get(cr, uid, 'product.fields')
        vals['sequence'] = sequence

        id = super(product_fields, self).create(cr, uid, vals, context)
        return id


    def unlink(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Warning !'), _('You can\'t delete this field'))


    def write(self, cr, uid, ids, vals, context=None):
        values = {}
        
        if 'required' in vals:
            values['required'] = vals['required']
        if 'translate' in vals:
            values['translate'] = vals['translate']

        id = super(product_fields, self).write(cr, uid, ids, values, context)
        return id


product_fields()