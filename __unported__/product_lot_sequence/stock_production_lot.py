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

"""Creates prodlot sequence chooose product sequence"""

from osv import osv

class stock_production_lot(osv.osv):

    _inherit = "stock.production.lot"

    def make_sscc(self, cr, uid, context={}):
        """return production lot number"""
        if context.get('product_id', False):
            sequence_obj_id = self.pool.get('product.product').browse(cr, uid, context['product_id']).sequence_id
            if sequence_obj_id:
                sequence_id = sequence_obj_id.id
                sequence_number = self.pool.get('ir.sequence').get_id(cr, uid, sequence_id)
                return sequence_number

        sequence = self.pool.get('ir.sequence').get(cr, uid, 'stock.lot.serial')
        return sequence

    _defaults = {
        'name': make_sscc
    }

stock_production_lot()