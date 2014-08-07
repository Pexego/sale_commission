# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Pexego (<www.pexego.es>). All Rights Reserved
#    $Santiago Argüeso Armesto$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Picking Invoice Pricelist",
    "description" : """Takes the price from the customer pricelist when you are generating customer invoices from an out picking without related sale order """,
    "version" : "1.0",
    "author" : "Pexego",
    "depends" : ["base","stock","sale"],
    "category" : "Stock",
    "init_xml" : [],
    "update_xml" : [],
    'demo_xml': [],
    "website": 'http://www.pexego.es',
    'installable': False,
    'active': False,
}
