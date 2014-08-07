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
from tools.translate import _

class pos_order(osv.Model):
    """ Modificaciones de pos order para indicar la mesa de facturacion. """
    _inherit = "pos.order"

    _columns = {
        'zone_id': fields.many2one('pos.category_place', 'Area', 
        required=True, readonly=False),
        'place_id': fields.many2one('pos.place', 'Table or room', 
        required=True, readonly=False),
    }

pos_order()

class pos_category_place(osv.Model):
    _name = 'pos.category_place'
    _description = "Information Area"
    _order = "name desc"
    
    _columns = {
        'sequence': fields.integer('Order', select=True),
        'name': fields.char('Name', size=64, required=True),   
        'sale_journal_id' : fields.many2one('account.journal',
         'Invoice Journal'),     
        'sale_simple_journal_id' : fields.many2one('account.journal',
         'Journal simplified billing'),
        'journal_ids': fields.one2many('account.journal', 'zone_id', 
        string='Daily payment', domain=[('type','in',['cash', 'bank'])]),
        'printer': fields.char('Printer', size=64,
         help=_("Nombre de la impresora por la que se va imprimir.")),
        'ticket': fields.boolean('Ticket format?'),
        'imagen': fields.binary('Image'),
    }

pos_category_place()

class pos_place(osv.Model):
    _name = 'pos.place'
    _description = "Table or room"
    _order = "name desc"
    
    _columns = {
        'name': fields.char('Reference', size=64, required=True),
        'category' : fields.many2one('pos.category_place', 'Area'),
        'imagen': fields.binary('Image'),
    }
pos_place()

class product_product(osv.Model):
    _inherit = 'product.product'
    
    _columns = {
        'category' : fields.many2one('pos.category_place',
         'Appear in the initial list of'),
    }
product_product()

class cancel_code(osv.Model):
    _inherit = "res.users"
    
    _columns = {
        'pos_code': fields.integer('Code', size=64),
    }
    _sql_constraints = [('pos_code_uniq','unique(pos_code)',
     'POS code number must be unique!')]
    
cancel_code()
