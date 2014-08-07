# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
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

from osv import osv

class stock_picking(osv.osv):

    _inherit = "stock.picking"

    def action_assign(self, cr, uid, ids, *args):
        """ Try to confirm all moves to check availability."""
        for pick in self.browse(cr, uid, ids):
            for move in pick.move_lines:
                if move.state in ['waiting','draft']:
                    move.write({'state':'confirmed'})

        return super(stock_picking, self).action_assign(cr, uid, ids, *args)

stock_picking()
