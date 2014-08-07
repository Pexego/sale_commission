# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Alejandro Núñez Liz$
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

from osv import osv, fields
from tools import ustr

class sale_order(osv.osv):
    """ Modificaciones de sale order para añadir la posibilidad de versionar el pedido de venta. """
    _inherit = "sale.order"
    
    def action_previous_version(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        
        sale_obj = self.browse(cr, uid, id, context=context)
        sale_ids = []
        for sale in sale_obj:
            vals = {}
            if not sale.sale_version_id:
                vals.update({'sale_version_id':sale.id,
                            'version': 1})
            else:
                vals.update({'version': sale.version + 1})
            new=self.copy(cr, uid, sale.id, vals)
            if not sale.sale_version_id:
                self.write(cr, uid, [new], {'name': sale.name + u" V.1"})
            else:
                self.write(cr, uid, [new], {'name': sale.sale_version_id.name + u" V." + ustr(sale.version + 1)})
            sale.write({'active': False})
            sale_ids.append(new)
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'sale', 'view_order_form')
        res_id = res and res[1] or False,
        
        return {
            'name': 'Sale Order',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': res_id,
            'res_model': 'sale.order',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': sale_ids and sale_ids[0] or False,
        }
        
    def _get_version_ids(self, cr, uid, ids, field_name, arg, context=None):
        if context is None: context = {}
        res = {}
        for sale in self.browse(cr, uid, ids):
            if sale.sale_version_id:
                res[sale.id] = self.search(cr, uid, ['|',('sale_version_id','=',sale.sale_version_id.id), ('id','=',sale.sale_version_id.id), ('version','<',sale.version), '|',('active','=',False),('active','=',True)])
            else:
                res[sale.id] = []
        return res
            

    _columns = {
        'sale_version_id': fields.many2one('sale.order', 'Orig version', required=False, readonly=False),
        'version': fields.integer('Version no.', readonly=True),
        'active': fields.boolean('Active', readonly=False, help="It indicates that the sales order is active."),
        'version_ids': fields.function(_get_version_ids, method=True, type="one2many", relation='sale.order', string='Versions', readonly=True)
    }
    _defaults = {
        'active': True,
        'version': 0
    }

sale_order()
