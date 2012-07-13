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

from django.template import Library
from django.core.urlresolvers import reverse
from pos import models as posmodels

register = Library()

def add_product_to_order_line(product=None, mesa=None):
    mesa = int(mesa)
    pos_order = posmodels.Pos_Order.objects.get(lugar=mesa)
    if request.method == 'POST':
        try:
            pos_order_line = posmodels.Pos_Order_Line.objects.get(clave=pos_order)
            pos_order_line.cantidad = (pos_order_line.cantidad + 1)
            #~ pos_order_line['cantidad'] = pos_order_line['cantidad'] + 1
            pos_order_line.save()
        except:
            pos_order_line = posmodels.Pos_Order_Line(clave=pos_order)
            pos_order_line.product_id = int(product.id)
            pos_order_line.product_name = product.name
            pos_order_line.cantidad = 1
            pos_order_line.descuento = 0.0
            pos_order_line.precio = product.lst_price
            pos_order_line.save()

    return reverse('place', args=[mesa])
    
register.simple_tag(add_product_to_order_line)
