***
Mini manual
***

NECESITA COMO DEPENDENCIA restaurant_pos ( módulo de OpenERP 6.1 )
Y la aplicación django necesitas las siguientes apps:
dajax  -> http://www.dajaxproject.com/
dajaxice -> http://www.dajaxproject.com/
inplaceeditform -> http://pypi.python.org/pypi/django-inplaceedit/0.83


Es necesario modificar en el fichero settings.py las siguientes líneas:

ENABLE_ERP = True  # Si se pone a False, no se realiza la conexión con el ERP
ERP_CONF = "RUTA AL FICHERO DE CONFIGURACIÓN DEL ERP"
ERP_PATH = "RUTA A LA CARPETA server de OPENERP, RUTA COMPLETA"
ERP_UN = 'admin' # Usuario de OPENERP con permisos
ERP_PW = 'admin' # Contraseña del usuario de OPENERP
ERP_DB = 'database' # Nombre de la base de datos

Y en el fichero de configuración del OpenERP, normalmente en ../server/install/openerp-server.conf

db_host = localhost # Host del servidor
db_port = False # Puerto del servidor
db_user = openerp # Usuario de PostgreSQL
db_password = openerp # Contraseña del usuario de PostgreSQL
addons_path = RUTA de nuestros módulos, localización española, addons, web addons y otros módulos que podamos necesitar, para precargarlos en la aplicación.


Saludos.

