# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Alejandro Núñez Liz$
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

class pos_order(osv.osv):
    """ Modificaciones de sale order para añadir la posibilidad de versionar el pedido de venta. """
    _inherit = "pos.order"

    _columns = {
        'place_id': fields.many2one('pos.place', 'Lugar', required=True, readonly=False),
    }

pos_order()

class pos_place(osv.osv):
    _name = 'pos.place'
    _description = "Place in the restaurant"
    _order = "name desc"
    
    _columns = {
        'name': fields.char('Place Ref', size=64, required=True),
        'price_increase': fields.float(string='Price increase', digits=(16, 2), required=False),
    }
    
pos_place()
