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

"""inherit res.partner for adds the functionally that a partner have a location"""

from osv import osv, fields

class res_partner(osv.osv):
    """inherit res.partner for adds the functionally that customer has a location"""
    _inherit = 'res.partner'

    _columns = {
        'create_customer_location': fields.boolean('Create customer location', help="If check creates a location if not exists for this customer to follow sent goods.")
    }

    _defaults = {
        'create_customer_location': lambda *a: True
    }

    def _set_partner_customer_location(self, cr, uid, partner_id, context=None):
        """creates customer location for partner in arguments"""
        if context is None: context = {}
        
        partner_id_obj = self.browse(cr, uid, partner_id)

        #checks if already exists partner location
        locations = self.pool.get('stock.location').search(cr, uid, [('partner_id', '=', partner_id)])

        if not locations:
            #creates a customer location for a specific partner if the partner is a costumer
            partner_location_id = self.pool.get('stock.location').create(cr, uid, vals = {
                                                        'location_id': partner_id_obj.property_stock_customer and partner_id_obj.property_stock_customer.id or False,
                                                        'name':partner_id_obj.name,
                                                        'usage': 'customer',
                                                        'partner_id': partner_id,
                                                        'company_id': self.pool.get('res.users').browse(cr, uid, uid).company_id.id
                                                    }, context=context)

            #updates the property of stock customer location for partner
            self.write(cr, uid, partner_id, vals={
                            'property_stock_customer': partner_location_id,
                        }, context=context)

        return True

    def create(self, cr, uid, vals, context=None):
        """Check to create customer location"""
        if context is None: context = {}
        partner_id = super(res_partner, self).create(cr, uid, vals, context = context)

        if vals.get('create_customer_location', False):
            self._set_partner_customer_location(cr, uid, partner_id, context=context)
            
        return partner_id

    def write(self, cr, uid, ids, vals, context=None):
        """Check to create customer location"""
        if context is None: context = {}
        res = super(res_partner, self).write(cr, uid, ids, vals, context = context)

        if vals.get('create_customer_location', False):
            if isinstance(ids, (int, long)):
                ids = [ids]
                
            for partner_id in ids:
                self._set_partner_customer_location(cr, uid, partner_id, context=context)

        return res

res_partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
