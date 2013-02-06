# -*- coding: utf-8 -*-
from django.conf import settings
import sys, os
import warnings
warnings.filterwarnings("ignore", message="Old style callback, usecb_func(ok, store) instead")


ERP_PATH = settings.ERP_PATH
if not ERP_PATH in sys.path:
    sys.path.insert(0, os.path.dirname(ERP_PATH))

from openerp.tools import config
from openerp.modules import get_modules
from openerp.pooler import get_db_and_pool

# Configurar el server con los parametros adecuados.
config.parse_config(['-c', settings.ERP_CONF])

# Modulos en nuestra conf de OpenERP
get_modules()

DB, POOL = get_db_and_pool(settings.ERP_DB)

cursor = DB.cursor()

user_obj = POOL.get('res.users')


try:
    USER = user_obj.search(cursor, 1, [
            ('login', '=', settings.ERP_UN),
            ], limit=1)[0]
except:
    cursor.rollback()
finally:
    cursor.close()
    
