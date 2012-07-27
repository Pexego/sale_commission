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
import time
from osv import osv,fields

class sequence(osv.osv):
    _inherit = "ir.sequence"
      
    def _get_code(self,cr,uid,num):
        keyword=self.pool.get('res.users').browse(cr,uid,uid).company_id.keyword
        val1 =keyword and keyword[int(num[0])] or num[0]
        val2 = keyword and keyword[int(num[1])] or num[1]
        return val1 + val2

    def _process_extend(self,cr,uid,s):
        
        return (s or '') % {
            'year':time.strftime('%Y'),
            'month': time.strftime('%m'),
            'day':time.strftime('%d'),
            'y': time.strftime('%y'),
            'doy': time.strftime('%j'),
            'woy': time.strftime('%W'),
            'weekday': time.strftime('%w'),
            'h24': time.strftime('%H'),
            'h12': time.strftime('%I'),
            'min': time.strftime('%M'),
            'sec': time.strftime('%S'),
            'kw_month': self._get_code(cr,uid,time.strftime('%m')),
            'kw_year':self._get_code(cr,uid,time.strftime('%y'))
        }
    def get_id(self, cr, uid, sequence_id, test='id', context=None):
        assert test in ('code','id')
        company_ids = self.pool.get('res.company').search(cr, uid, [], context=context)
        cr.execute('''SELECT id, number_next, prefix, suffix, padding
                      FROM ir_sequence
                      WHERE %s=%%s
                       AND active=true
                       AND (company_id in %%s or company_id is NULL)
                      ORDER BY company_id, id
                      FOR UPDATE NOWAIT''' % test,
                      (sequence_id, tuple(company_ids)))
        res = cr.dictfetchone()
        if res:
            cr.execute('UPDATE ir_sequence SET number_next=number_next+number_increment WHERE id=%s AND active=true', (res['id'],))
            if res['number_next']:
                return self._process_extend(cr,uid,res['prefix']) + '%%0%sd' % res['padding'] % res['number_next'] + self._process_extend(cr,uid,res['suffix'])
            else:
                return self._process_extend(cr,uid,res['prefix']) + self._process_extend(cr,uid,res['suffix'])
        return False
  

sequence()