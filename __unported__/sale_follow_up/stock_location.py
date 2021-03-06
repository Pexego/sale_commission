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

"""inherit stock.location, add the posubility that a location belongs to a partner"""

from osv import fields, osv

class stock_location(osv.osv):
    """inherit stock.location, add the posubility that a location belongs to a partner"""
    _inherit = 'stock.location'

    _columns = {
            'partner_id': fields.many2one('res.partner', "Owner", ondelete='cascade'),
        }
        
stock_location()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: