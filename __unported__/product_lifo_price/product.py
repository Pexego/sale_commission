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

from osv import osv, fields

#----------------------------------------------------------
# Products
#----------------------------------------------------------
class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        'cost_method': fields.selection([('standard','Standard Price'), ('average','Average Price'), ('lifo', 'LIFO Price')], 'Costing Method', required=True,
            help="Standard Price: the cost price is fixed and recomputed periodically (usually at the end of the year), Average Price: the cost price is recomputed at each reception of products, LIFO Price: the cost price is the price of last reception of products."),
    }

    _defaults = {
        'cost_method': lambda *a: 'standard',
    }


product_template()