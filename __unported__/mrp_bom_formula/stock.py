# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2012 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#    $Marta Vázquez Rodríguez$
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
from osv import osv, fields
import tools

class stock_production_lot(osv.osv):
    _inherit = "stock.production.lot"
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):

        if context is None:
            context = {}
        result = super(osv.osv, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar=toolbar)

        if view_type == 'form':

            if context.get('product_id',False):
                product_fields = self.pool.get('product.fields').search(cr, uid, [('product_id', '=',  context['product_id'])])
            else:
                product_fields = self.pool.get('product.fields').search(cr, uid, [])

            if product_fields:
                view_part = u''
                field_names = []
                for prod_fi in self.pool.get('product.fields').read(cr, uid, product_fields, ['field_id', 'sequence','product_id']):
                    if prod_fi['product_id']:



                        #Sequence fields
                        prod_fields = [{'sequence':prod_fi['sequence'], 'id':prod_fi['id'],'field_id':prod_fi['field_id']}]
                        fields = sorted(prod_fields, key=lambda k: k['sequence'])

                        pfields = []
                        for field in fields:
                            pfields.append(field['field_id'])

                        #Create new view - fields
                        for pfield in pfields:
                            product_field = self.pool.get('ir.model.fields').browse(cr, uid, pfield[0])
                            if str(product_field.name).startswith('x_'):
                                field_names.append(product_field.name)
                                if context.get('product_id',False):
                                    view_part+= u'<field name="%s"' % product_field.name
                                    view_part+= u'/>\n'
                                else:
                                    view_part+= u'<field name="%s"' % product_field.name
                                    view_part+= u""" attrs="{'invisible':[('product_id','not in',["""+u",".join(tools.ustr(x) for x in prod_fi['product_id'])+u"""])]}" modifiers="{&quot;invisible&quot;: [[&quot;product_id&quot;, &quot;not in&quot;, ["""+u",".join(tools.ustr(x) for x in prod_fi['product_id'])+u"""]]]}"/>\n"""


                result['fields'].update(self.fields_get(cr, uid, field_names, context))
                result['arch'] = result['arch'].decode('utf8').replace('<page string="field_new"/>', '<page string="Fields of product" invisible="0">'+view_part+'</page>')
               
            else:
                result['arch'] = result['arch'].replace('<page string="field_new"/>', "")

        return result




stock_production_lot()