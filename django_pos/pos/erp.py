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

from django.conf import settings
import sys, os
import warnings

warnings.filterwarnings("ignore", message="Old style callback, usecb_func(ok, store) instead")

ERP_PATH = settings.ERP_PATH
if not ERP_PATH in sys.path:
    sys.path.insert(0, os.path.dirname(ERP_PATH))

from openerp.tools import config
#from openerp.modules import get_modules
from openerp.pooler import get_db_and_pool

# Configurar el server con los parametros adecuados.
config.parse_config(['-c', settings.ERP_CONF])

# Modulos en nuestra conf de OpenERP
#get_modules()

DB, POOL = get_db_and_pool(settings.ERP_DB)
CURSOR = DB.cursor()
user_obj = POOL.get('res.users')

try:
    # El usuario 1 es el admin
    USER = user_obj.search(CURSOR, 1, [
            ('login', '=', settings.ERP_UN),
            ], limit=1)[0]
except:
    CURSOR.rollback()
    CURSOR.close()
finally:
    pass
