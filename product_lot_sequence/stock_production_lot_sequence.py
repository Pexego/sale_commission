# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Pexego Sistemas Informáticos. All Rights Reserved
#    $Id$
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

"""
Manages prodlots sequences by product
"""

import pooler

_sequences_cache = {}

def get_default_seq_id(cr, uid, seq_name = u'COD', name = "Production Lots", seq_code = 'stock.lot.serial', company_id=False):
    """
    Get by default a sequence for active product.
    If the sequence not exists it creates.
    """
    pool = pooler.get_pool(cr.dbname)

    if company_id:
        #cache system for massive creation of sequences
        if not _sequences_cache.get(company_id):
            _sequences_cache[company_id] = {}

        if _sequences_cache[company_id].get(seq_name):
            return _sequences_cache[company_id][seq_name]

    sequence_ids = pool.get('ir.sequence').search(cr, uid, [('code', '=', seq_code), ('name', '=', name)])
    if sequence_ids:
        sequence_id = sequence_ids[0]
    else:
        #
        # Creamos una nueva secuencia
        #
        sequence_id = pool.get('ir.sequence').create(cr, uid, {
            'name': name,
            'code': seq_code,
            'padding': 3,
            'prefix': u"L%(doy)s%(y)s (" + seq_name,
            'suffix': ")",
            'company_id': company_id
        })

    _sequences_cache[company_id][seq_name] = sequence_id

    return sequence_id