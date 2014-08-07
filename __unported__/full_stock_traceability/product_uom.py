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

"""Adds new method to return base uom from same category"""

from osv import osv
from tools.translate import _

class product_uom(osv.osv):
    """Adds new method to return base uom from same category"""

    _inherit = "product.uom"

    def get_base_uom(self, cr, uid, orig_uom, context=None):
        """Returns base uom from same category"""
        if context is None: context = {}

        uom_ids = self.search(cr, uid, [('category_id', '=', orig_uom.category_id.id), ('uom_type', '=', 'reference')])
        if not uom_ids:
            raise osv.except_osv(_('Error!'),
                _(u'There isn\'t reference uom for this category: %s.' % orig_uom.category_id.name))
        elif len(uom_ids) > 1:
            raise osv.except_osv(_('Error!'),
                _(u'There are more that one reference uom for this category: %s.' % orig_uom.category_id.name))

        return uom_ids[0]

product_uom()
