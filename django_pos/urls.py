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

from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

js_info_dict = {
    'packages': ('django.conf',),
}

urlpatterns = patterns('',
    
    url(r'^inplaceeditform/', include('inplaceeditform.urls')),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
    
    url(r'^$', 'pos.views.home', name='home'),
    url(r'^(?P<mesa>[-\d]+)/$', 'pos.views.products', name='place'),
    url(r'^(?P<mesa>[-\d]+)/pagar/(?P<tipo>[-\d]+)/$', 'pos.views.pagar', name='pagar'),
    url(r'^(?P<mesa>[-\d]+)/pagar/(?P<tipo>[-\d]+)/validado/$', 'pos.views.validar_pago', name='validar'),
    url(r'^(?P<mesa>[-\d]+)/category/(?P<id>[-\d]+)/$', 'pos.views.category', name='category'),
    
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
    # url(r'^point_of_sale/', include('pos.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$',
     'django.views.static.serve',
     {'document_root': settings.MEDIA_ROOT}),
)
