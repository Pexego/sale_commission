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

"""adds functionally on product object from block prodlots"""

from osv import fields, osv

class product_template(osv.osv):
    """adds functionally on product object from block prodlots"""
    _inherit = "product.template"
    
    _columns = {
            'property_waste': fields.property(
            'stock.location',
            type='many2one',
            relation='stock.location',
            string="Waste Location",
            method=True,
            view_load=True,
            help="For the current product (template), this stock location will be used, instead of the default one, as a virtual location where the products go when remove"),
            }

product_template()