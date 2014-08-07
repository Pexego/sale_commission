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

"""add functionally for differentiate miscible products and not"""

from osv import fields, osv
from tools.translate import _

class product_product(osv.osv):
    """add functionally for differentiate miscible product and not miscible product"""
    _inherit = "product.product"
    
    _columns = {
                'miscible': fields.boolean('Miscible Product', help="If the product can be mixed check this, for not create a procurement in a production order, and can put inside mix locations and only these."),
                'not_do_procurement': fields.boolean('Don\'t procurement in production', help="If check, in production, if not is a miscible product won't do a procurement move."),
                'track_all': fields.boolean('Track All Lots' , help="Forces to specify a Production Lot for all moves containing this product. This will also disable auto picking")
                }
    _defaults = {
                 'miscible': lambda *a: 0,
                 'not_do_procurement': lambda *a: 0,
                 }

    def check_if_procurement(self, cr, uid, ids, vals):
        """checks if the product has configurate well the procurement"""
        if vals.get('miscible', False) and not vals.get('not_do_procurement', False):
            raise osv.except_osv(_('Error!'),
                _('Cannnot put this product to do procurement, because this poduct is marked as miscible and the miscible products don\'t do procurement.'))
        return True

    def write(self, cr, uid, ids, vals, context={}):
        """overwrites write method for checks if the procurement for the product is configurate well"""
        self.check_if_procurement(cr, uid, ids, vals)

        if vals.get('track_all', False):
            vals.update({ 'track_production' : True, 'track_incoming' : True, 'track_outgoing' : True})

        return super(product_product, self).write(cr, uid, ids, vals, context=context)

    def create(self, cr, uid, vals, context={}):
        """overwrites create method for checks if the procurement for the product is configurate well and creates sequence to production lots"""
        self.check_if_procurement(cr, uid, [], vals)

        if vals.get('track_all', False):
            vals.update({ 'track_production' : True, 'track_incoming' : True, 'track_outgoing' : True})

        return super(product_product, self).create(cr, uid, vals, context=context)


product_product()

class product_template(osv.osv):
    """add functionally for differentiate miscible product and not miscible product"""
    _inherit = "product.template"

    _columns = {
        'property_raw': fields.property(
            'stock.location',
            type='many2one',
            relation='stock.location',
            string="Raw Materials Location",
            method=True,
            view_load=True,
            help="For the current product (template), this stock location will be used, instead of the default one, as the source where search the products needs for a production of this product (template)."),
        'property_mix': fields.property(
            'stock.location',
            type='many2one',
            relation='stock.location',
            string='Mix Moves Location',
            method=True,
            view_load=True,
            help="Location where will go the products that form a mix")
        }

product_template()