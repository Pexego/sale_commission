# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Pexego (<www.pexego.es>). All Rights Reserved
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

"""add lot sequence field in products"""

from osv import osv, fields
from stock_production_lot_sequence import get_default_seq_id

class product_product(osv.osv):
    """add lot sequence field in products"""
    
    _inherit = "product.product"

    _columns = {
                'sequence_id':fields.many2one('ir.sequence', 'Prodlots Serial'),
                }

    _defaults = {
                    'default_code': lambda *a: 'COD',
                    'sequence_id': lambda x, y, z, c: get_default_seq_id(y, z, company_id=x.pool.get('res.users').browse(y,z,z).company_id.id),
                 }

    def create(self, cr, uid, vals, context={}):
        """overwrites create method to create new sequence to production lots"""
        product_id = super(product_product, self).create(cr, uid, vals, context=context)
        product = self.browse(cr, uid, product_id)
        #Manages the sequence number
        if not vals.get('sequence_id'):
            sequence_id = get_default_seq_id(cr, uid, product.default_code, product.name, company_id=product.company_id and product.company_id.id or False)
            if sequence_id:
                self.write(cr, uid, [product_id], {'sequence_id': sequence_id})

        return product_id

product_product()