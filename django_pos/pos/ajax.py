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

from django.core.urlresolvers import reverse
from dajaxice.decorators import dajaxice_register
from pos import models as posmodels

@dajaxice_register
def add_product_to_order_line(request, product_id, product_name, price, mesa):
    mesa = int(mesa)
    product_id = int(product_id)
    price = price.replace(",",".")
    pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
    pos_order = pos_order[0]
    try:
        pos_order_lines = posmodels.Pos_Order_Line.objects.filter(clave=pos_order)
        valor= 0
        for line in pos_order_lines:
            if line.product_id == product_id:
                valor=1
                line.cantidad = (line.cantidad + 1)
                line.save()
        if valor == 0:
            pos_order_line = posmodels.Pos_Order_Line(clave=pos_order)
            pos_order_line.product_id = int(product_id)
            pos_order_line.product_name = product_name
            pos_order_line.cantidad = 1
            pos_order_line.descuento = 0.0
            pos_order_line.precio = price
            pos_order_line.save()
    except:
        pos_order_line2 = posmodels.Pos_Order_Line(clave=pos_order)
        pos_order_line2.product_id = int(product_id)
        pos_order_line2.product_name = product_name
        pos_order_line2.cantidad = 1
        pos_order_line2.descuento = 0.0
        pos_order_line2.precio = price
        pos_order_line2.save()
        
    
    return reverse('place', args=[mesa])
