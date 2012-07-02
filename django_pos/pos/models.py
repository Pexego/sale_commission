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

from django.db import models
from django.utils.translation import ugettext_lazy as _

# POS ORDER

class Pos_Order(models.Model):
    """
    Pos Order
    """
    lugar = models.IntegerField(verbose_name=_('Place'))
    tipo_pago = models.CharField(max_length=255, verbose_name=_('Tipo pago'))
    creada = models.DateTimeField(auto_now_add=True, verbose_name=_('Created on'))
    cerrada = models.DateTimeField(auto_now_add=True, verbose_name=_('Closed on'))
    pagada = models.BooleanField(default=False, verbose_name=_('Pagada'))
    
    class Meta:
        verbose_name = _(u'Pos Order')
        verbose_name_plural = _(u'Pos Order')
    
    @property
    def products(self):
        products = Pos_Order_Line.objects.filter(clave=self)
        return products
    
    @property
    def total(self):
        total=0.0
        for p in self.products:
            total = total + p.total
        return total

    def __unicode__(self):
        return "venta"

class Pos_Order_Line(models.Model):
    """
    Pos Order Line
    """
    clave = models.ForeignKey(Pos_Order, related_name="productos")
    product_id = models.IntegerField(verbose_name=_('product id'), null=True)
    product_name = models.CharField(max_length=255, verbose_name=_('product'), null=True)
    cantidad = models.IntegerField(verbose_name=_('cantidad'), null=True)
    descuento = models.FloatField(default=0.0, verbose_name=_('descuento'), null=True)
    precio = models.FloatField(default=0.0, verbose_name=_('precio'), null=True)
    
    class Meta:
        verbose_name = _(u'PoS order line')
        verbose_name_plural = _(u'PoS order line')
    
    @property
    def total(self):
        total = (self.cantidad * self.precio) - ((self.cantidad * self.precio)*(self.descuento/100))
        return total
    
    def __unicode__(self):
        return self.product_name
