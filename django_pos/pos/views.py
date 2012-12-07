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

def search(request, mesa):
    query = request.GET.get('q', '')
    context={}
    mesa = int(mesa)
    from erp import POOL, DB, USER
    product_obj = POOL.get('product.product')
    pago_obj = POOL.get("account.bank.statement")
    category_obj = POOL.get('pos.category')
    cursor = DB.cursor()
    try:
        pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
        pos_order = pos_order[0]
    except:
        pos_order = posmodels.Pos_Order(lugar=mesa, tipo_pago="Caja")
        pos_order.save()
        
    context['pos_order'] = pos_order
    context['mesa'] = mesa
    #print query
    try:
        if query:
            products_ids = product_obj.search(cursor, USER, [('qty_available', '>', 0.0),('pos_categ_id', '!=', None),('name', 'ilike', query)], order="name DESC")
        else:
            products_ids = product_obj.search(cursor, USER, [('qty_available', '>', 0.0),('pos_categ_id', '!=', None)], order="name DESC")
        
        context['products'] = product_obj.browse(cursor, USER, products_ids)        
        caterogies_ids = category_obj.search(cursor, USER, [('parent_id', '=', False )], order="name DESC")
        context['caterogies'] = category_obj.browse(cursor, USER, caterogies_ids)
        pago_ids = pago_obj.search(cursor, USER, [('state','=','open')])
        context['metodos_pago'] = pago_obj.browse(cursor, USER, pago_ids)
        return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))
    except Exception as e:        
        pass
    finally:
        cursor.commit()
        cursor.close()
    return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))


def products(request, mesa):
    context={}
    mesa = int(mesa)    
    from erp import POOL, DB, USER
    
    product_obj = POOL.get('product.product')
    pago_obj = POOL.get("account.bank.statement")
    category_obj = POOL.get('pos.category')
    cursor = DB.cursor()
    
    try:
        pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
        pos_order = pos_order[0]
    except:
        pos_order = posmodels.Pos_Order(lugar=mesa, tipo_pago="Caja")
        pos_order.save()
        
    context['pos_order'] = pos_order
    context['mesa'] = mesa
    
    try:
        products_ids = product_obj.search(cursor, USER, [('qty_available', '>', 0.0),('pos_categ_id', '!=', None),('favorite', '=', True)], order="name DESC")
        caterogies_ids = category_obj.search(cursor, USER, [('parent_id', '=', False )], order="name DESC")
        context['products'] = product_obj.browse(cursor, USER, products_ids)
        context['caterogies'] = category_obj.browse(cursor, USER, caterogies_ids)
        pago_ids = pago_obj.search(cursor, USER, [('state','=','open')])
        context['metodos_pago'] = pago_obj.browse(cursor, USER, pago_ids)
        return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))
    except Exception as e:
        
        pass
    finally:
        cursor.commit()
        cursor.close()

    return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))

def category(request, mesa, id):
    context={}
    p_id = int(id)
    mesa = int(mesa)
    from erp import POOL, DB, USER
    
    product_obj = POOL.get('product.product')
    pago_obj = POOL.get("account.bank.statement")
    category_obj = POOL.get('pos.category')
    cursor = DB.cursor()
    
    try:
        pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
        pos_order = pos_order[0]
    except:
        pos_order = posmodels.Pos_Order(lugar=mesa, tipo_pago="Caja")
        pos_order.save()
        
    context['pos_order'] = pos_order
    context['mesa'] = mesa
    
    try:
        products_ids = product_obj.search(cursor, USER, [('pos_categ_id', '=', p_id)], order="name DESC")
        context['products'] = product_obj.browse(cursor, USER, products_ids)
        caterogies_ids = category_obj.search(cursor, USER, [('parent_id', '=', p_id )], order="name DESC")
        context['caterogies'] = category_obj.browse(cursor, USER, caterogies_ids)
        pago_ids = pago_obj.search(cursor, USER, [('state','=','open')])
        context['metodos_pago'] = pago_obj.browse(cursor, USER, pago_ids)
        return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))
    except Exception as e:
        
        pass
    finally:
        cursor.commit()
        cursor.close()

    return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))

def home(request, seccion):
    context={}
    username = settings.ERP_UN
    password = settings.ERP_PW
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
        
    from erp import POOL, DB, USER
    
    place_obj = POOL.get('pos.place')
    cursor = DB.cursor()
    

    pos_order = posmodels.Pos_Order.objects.filter(pagada=False)
    ocupadas = []
    for mesa in pos_order:
        ocupadas.append(mesa.lugar)
    context['ocupadas']=ocupadas
    try:
        if seccion == "1":
            place_ids = place_obj.search(cursor, USER, [('location_table','=', True),], order="name DESC")
        else:
            place_ids = place_obj.search(cursor, USER, [('location_table','=', False),], order="name DESC")
        context['places'] = place_obj.browse(cursor, USER, place_ids)
        return render_to_response('pos/inicio.html', context, context_instance=RequestContext(request))
    except Exception as e:
        
        pass
    finally:
        cursor.commit()
        cursor.close()

    return render_to_response('pos/inicio.html', context, context_instance=RequestContext(request))

def selector(request):
    context={}
    return render_to_response('pos/selector.html', context, context_instance=RequestContext(request))  


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
    
    context["result"]= 0.0
    context["pagado"]=0.0
    if request.method == 'POST':
        pagado = request.POST.get("pagado")
        pagado = pagado.replace(",",".")
        try:
            pagado = float(pagado)
            if pagado != 0.0:
                context["pagado"] = pagado
                context["result"] = pagado - pos_order.total
        except:
            pass
    
    return render_to_response('pos/validar.html', context, context_instance=RequestContext(request))


def validar_pago(request, mesa, tipo):
    context={}
    mesa = int(mesa)
    tipo = int(tipo)
    from erp import POOL, DB, USER
    
    pos_obj = POOL.get('pos.order')
    cursor = DB.cursor()
    
    try:
        pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
        pos_order = pos_order[0]
        context['pos_order'] = pos_order
        context['mesa'] = mesa
        pos_created = pos_obj.create(cursor, USER, {'place_id':mesa,}, context=context)
        order_line_obj = POOL.get("pos.order.line")
        for p in pos_order.products:
            order_line = order_line_obj.create(cursor, USER, {
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
        pos_obj.add_payment(cursor, USER, pos_created, data, context=context)
        cursor.commit()
        pos_order.pagada = True
        pos_order.save()
    
    except Exception as e:        
        cursor.rollback()
        pass
    finally:
        cursor.commit()
        cursor.close()

    return render_to_response('pos/pay.html', context, context_instance=RequestContext(request))

def borrar_mesa(request, mesa, code):
    context={}
    mesa = int(mesa)
    from erp import POOL, DB, USER
    pos_obj = POOL.get('pos.order')
    user_obj = POOL.get('res.users')
    cursor = DB.cursor()
    try:
        user_ids = user_obj.search(cursor, USER, [('cancel_code','=', code),], order="name DESC")
        if user_ids:
            try:
                pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
                pos_order = pos_order[0]
                context['pos_order'] = pos_order
                context['mesa'] = mesa
                pos_created = pos_obj.create(cursor, USER, {'place_id':mesa,'note':code,}, context=context)
                
                order_line_obj = POOL.get("pos.order.line")
                for p in pos_order.products:
                    order_line = order_line_obj.create(cursor, USER, {
                        'product_id': p.product_id,
                        'price_unit': p.precio,
                        'qty': p.cantidad,
                        'discount': p.descuento,
                        'order_id': pos_created,
                    }, context=context)
                borrar = pos_obj.write(cursor, USER, [pos_created,], {'state': 'cancel'}, context=context)
                if borrar == True:
                    pos_order.delete()
                    cursor.commit()
            except Exception as e:        
                cursor.rollback()
                pass
            return render_to_response('pos/borrar.html', context, context_instance=RequestContext(request))
        else:
            return render_to_response('pos/no_borrar.html', context, context_instance=RequestContext(request))
    finally:
        cursor.commit()
        cursor.close()

def eliminar_producto(request, mesa, producto):
    context={}
    mesa = int(mesa)
    producto = int(producto)
    from erp import POOL, DB, USER
    
    product_obj = POOL.get('product.product')
    pago_obj = POOL.get("account.bank.statement")
    category_obj = POOL.get('pos.category')
    cursor = DB.cursor()
   
    try:
        pos_order = posmodels.Pos_Order.objects.filter(lugar=mesa).filter(pagada=False)
        pos_order = pos_order[0]
        for p in pos_order.products:
            if p.pk == producto:
                p.delete()
        pos_order.save()
    except:
        pass

    context['pos_order'] = pos_order
    context['mesa'] = mesa
    
    try:
        
        products_ids = product_obj.search(cursor, USER, [('qty_available', '>', 0.0),('pos_categ_id', '!=', None),('favorite', '=', True)], order="name DESC")
        context['products'] = product_obj.browse(cursor, USER, products_ids)
        caterogies_ids = category_obj.search(cursor, USER, [('parent_id', '=', False )], order="name DESC")
        context['caterogies'] = category_obj.browse(cursor, USER, caterogies_ids)
        pago_ids = pago_obj.search(cursor, USER, [('state','=','open')])
        context['metodos_pago'] = pago_obj.browse(cursor, USER, pago_ids)
        return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))
    except Exception as e:
        pass
    finally:
        cursor.commit()
        cursor.close()
    return render_to_response('pos/products_list.html', context, context_instance=RequestContext(request))

def imprimir(request, pos_order):
    context={}
    pos_order = int(pos_order)
    try:
        pos_order = posmodels.Pos_Order.objects.get(pk=pos_order)
        context['pos_order'] = pos_order
    except Exception as e:
        pass
    return render_to_response('pos/ticket.html', context, context_instance=RequestContext(request))

def imprimir_prefactura(request, pos_order, mesa, paymet):
    context={}
    mesa = int(mesa)
    pos_order = int(pos_order)
    context['paymet'] = paymet
    context['mesa'] = mesa
    try:
        pos_order = posmodels.Pos_Order.objects.get(pk=pos_order)
        context['pos_order'] = pos_order
        
    except Exception as e:
        pass
    return render_to_response('pos/ticket_previopago.html', context, context_instance=RequestContext(request))

def open_cash(request):
    context = {}
    from erp import POOL, DB, USER
    pos_open_statement = POOL.get('pos.open.statement')
    cursor = DB.cursor()
    try:
        pos_open_statement.open_statement(cursor, USER, [], context=context)
        cursor.commit()
    except:
        cursor.rollback()
    finally:
        cursor.close()
    context={}
    return render_to_response('pos/selector.html', context, context_instance=RequestContext(request)) 
