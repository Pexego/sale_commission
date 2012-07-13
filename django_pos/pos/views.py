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

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from pos import models as posmodels
from django.contrib.auth import authenticate, login

def products(request, mesa):
    context={}
    mesa = int(mesa)
    from erp import POOL, DB, USER, CURSOR
    product_obj = POOL.get('product.product')
    pago_obj = POOL.get("account.bank.statement")
    try:
        pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
        pos_order = pos_order[0]
    except:
        pos_order = posmodels.Pos_Order(lugar=mesa, tipo_pago="Caja")
        pos_order.save()
        
    context['pos_order'] = pos_order
    context['mesa'] = mesa
    
    try:
        products_ids = product_obj.search(CURSOR, USER, [('qty_available', '>', 0.0),('pos_categ_id', '!=', None)], order="name DESC")
        context['products'] = product_obj.browse(CURSOR, USER, products_ids)
        pago_ids = pago_obj.search(CURSOR, USER, [('state','=','open')])
        context['metodos_pago'] = pago_obj.browse(CURSOR, USER, pago_ids)
        return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))
    except Exception as e:
        print e
        pass
    return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))

def category(request, mesa, id):
    context={}
    p_id = int(id)
    mesa = int(mesa)
    from erp import POOL, DB, USER, CURSOR
    product_obj = POOL.get('product.product')
    pago_obj = POOL.get("account.bank.statement")
    try:
        pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
        pos_order = pos_order[0]
    except:
        pos_order = posmodels.Pos_Order(lugar=mesa, tipo_pago="Caja")
        pos_order.save()
        
    context['pos_order'] = pos_order
    context['mesa'] = mesa
    
    try:
        products_ids = product_obj.search(CURSOR, USER, [('pos_categ_id', '=', p_id)], order="name DESC")
        context['products'] = product_obj.browse(CURSOR, USER, products_ids)
        pago_ids = pago_obj.search(CURSOR, USER, [('state','=','open')])
        context['metodos_pago'] = pago_obj.browse(CURSOR, USER, pago_ids)
        return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))
    except Exception as e:
        print e
        pass
    return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))

def home(request):
    context={}
    username = 'alejandro'
    password = 'm0n4MAR'
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
        
    from erp import POOL, DB, USER, CURSOR
    place_obj = POOL.get('pos.place')
    pos_order = posmodels.Pos_Order.objects.filter(pagada=False)
    ocupadas = []
    for mesa in pos_order:
        ocupadas.append(mesa.lugar)
    context['ocupadas']=ocupadas
    try:
        place_ids = place_obj.search(CURSOR, USER, [], order="name DESC")
        context['places'] = place_obj.browse(CURSOR, USER, place_ids)
        return render_to_response('pos/inicio.html', context, context_instance=RequestContext(request))
    except Exception as e:
        print e
        pass
        
    
    
    return render_to_response('pos/inicio.html', context, context_instance=RequestContext(request))


def pagar(request, mesa, tipo):
    context={}
    mesa = int(mesa)
    tipo = int(tipo)
    
    try:
        pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
        pos_order = pos_order[0]
    except:
        pass
        
    context['pos_order'] = pos_order
    context['mesa'] = mesa
    context['tipo'] = tipo
    
    context["result"]=0.0
    context["pagado"]=0.0
    if request.method == 'POST':
        pagado = request.POST.get("pagado")
        pagado = pagado.replace(",",".")
        pagado = float(pagado)
        if pagado != 0.0:
            context["pagado"] = pagado
            context["result"] = pagado - pos_order.total
    
    return render_to_response('pos/validar.html', context, context_instance=RequestContext(request))


def validar_pago(request, mesa, tipo):
    context={}
    mesa = int(mesa)
    tipo = int(tipo)
    from erp import POOL, DB, USER, CURSOR
    pos_obj = POOL.get('pos.order')
    try:
        pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
        pos_order = pos_order[0]
        context['pos_order'] = pos_order
        context['mesa'] = mesa
        pos_created = pos_obj.create(CURSOR, USER, {'place_id':mesa,}, context=context)
        order_line_obj = POOL.get("pos.order.line")
        for p in pos_order.products:
            order_line = order_line_obj.create(CURSOR, USER, {
                'product_id': p.product_id,
                'price_unit': p.precio,
                'qty': p.cantidad,
                'discount': p.descuento,
                'order_id': pos_created,
            }, context=context)
        data = {
            'journal': tipo,
            'amount': pos_order.total,
            'payment_name': "mesa %(mesa)s a las %(fecha)s" % {'mesa': mesa, 'fecha': pos_order.creada},
            'payment_date': pos_order.creada,
        }
        pos_obj.add_payment(CURSOR, USER, pos_created, data, context=context)
        CURSOR.commit()
        pos_order.pagada = True
        pos_order.save()
    except Exception as e:
        print e
        CURSOR.rollback()
        pass
    return render_to_response('pos/pay.html', context, context_instance=RequestContext(request))
