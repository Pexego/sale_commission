# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
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
from profiler import create_noupdate_field
import pooler

class init_noupdate(osv.osv):
    
    _name = "init.noupdate"
    _description = "Initialize noupdate fields in ir_model_data models"
    _auto = False
    
    def init(self, cr):
        cr.execute("select distinct model from ir_model_data")
        pool = pooler.get_pool(cr.dbname)
        models = cr.fetchall()
        for model in models:
            create_noupdate_field(cr, 1, model[0], pool)
            
        cr.execute("select model,res_id from ir_model_data where noupdate = True")
        records = cr.fetchall()
        for rec in records:
            obj = pool.get(rec[0])
            if obj:
                table = obj._table
            else:
                table = rec[0]
            cr.execute("select * from pg_tables where schemaname='public' and tablename = '%s'" % table)
            if cr.rowcount:
                cr.execute("update %s set x_noupdate = True where id = %d" % (table,rec[1]))
    
init_noupdate()
