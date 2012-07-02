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

from django.contrib import admin
from django.core.urlresolvers import reverse
from models import *

class Pos_Order_LineInline(admin.TabularInline):
    model = Pos_Order_Line
    extra = 1

class Pos_OrderAdmin(admin.ModelAdmin):
       
    list_display = ['lugar', 'creada','pagada']
    list_filter = ['lugar', 'creada', 'pagada']
    search_fields = ['lugar', 'pagada']

    inlines = [
        Pos_Order_LineInline,
    ]
    
admin.site.register(Pos_Order, Pos_OrderAdmin)
