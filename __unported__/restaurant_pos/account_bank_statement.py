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

from osv import fields, osv

class account_journal(osv.Model):
    _inherit = 'account.journal'
    _columns = {
        'zone_id' : fields.many2one('pos.category_place', 'Area'),     
    }

account_journal()

class account_cash_statement(osv.Model):
    _inherit = "account.bank.statement"
    
    _columns = {
        'user_open': fields.many2one('res.users', 'Opened cash'),
        'user_close': fields.many2one('res.users', 'Closed cash'),
    }
account_cash_statement()
