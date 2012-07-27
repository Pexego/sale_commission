# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-2011 Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
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

class mrp_bom(osv.osv):

    _inherit = "mrp.bom"
    _order = "bom_id,sequence"

    _columns = {
        'formula': fields.char('Formula', size=255),
        'eval_type': fields.selection([('fixed', 'Fixed'),('computed','Computed')], 'Computation', help="Evaluation type, fixed quantity or quantity over formula field"),
        'seq_lines_id': fields.many2one('ir.sequence', 'Sequence', readonly=True)
    }

    _defaults = {
        'eval_type': 'fixed'
    }

    def create(self, cr, uid, vals, context=None):
        if context is None: context = {}

        seq_id = self.pool.get('ir.sequence').search(cr, uid, [('code', '=', 'mrp.bom.seq')], order="id")
        if seq_id:
            vals['seq_lines_id'] = self.pool.get('ir.sequence').copy(cr, uid, seq_id[0], {'number_next': 1})

        if vals.get('bom_id', False):
            bom = self.browse(cr, uid, vals['bom_id'])
            if bom.seq_lines_id:
                num = self.pool.get('ir.sequence').get_id(cr, uid, bom.seq_lines_id.id)
                vals['sequence'] = num

        return super(mrp_bom, self).create(cr, uid, vals, context=context)

mrp_bom()