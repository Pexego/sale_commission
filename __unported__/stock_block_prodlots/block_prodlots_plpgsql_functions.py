# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 Pexego (<www.pexego.es>). All Rights Reserved
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

"""Creates functions to search prodlots to block"""

from osv import osv

class plpgsql_block_prodlots(osv.osv):
    """Creates functions to search prodlots to block"""
    _name = "plpgsql.block.prodlots"
    _description = "Creates functions to search prodlots to block"
    _auto = False

    def init(self, cr):
        """creates functions when install"""
        #check if exists the language plpgsql in bbdd, if not, is created for can create functions in this language
        cr.execute("select * from pg_language where lanname = 'plpgsql'")
        if not cr.rowcount:
            cr.execute("create language 'plpgsql'")

        #creates a function. From int parameter (prodlot_id) returns all prodlots child of specific
        cr.execute("""CREATE OR REPLACE FUNCTION block_prodlots_up(integer)
        RETURNS SETOF stock_production_lot AS
        $BODY$
            declare parent_move record;
                    child_prodlot record;
                    result record;
            BEGIN
                 FOR parent_move IN select distinct stock_move.* from stock_move
                 inner join stock_move_history_ids on stock_move.id = parent_id
                 where prodlot_id = $1 and state != 'cancel'
                 LOOP
                    FOR child_prodlot IN select distinct stock_production_lot.* from stock_move
                    inner join stock_move_history_ids on child_id = stock_move.id
                    inner join stock_production_lot on stock_production_lot.id = stock_move.prodlot_id
                    where parent_id = parent_move.id and stock_move.state != 'cancel' and stock_production_lot.id != $1
                    LOOP
                        FOR result in select distinct * from block_prodlots_up(child_prodlot.id)
                        LOOP
                            return next result;
                        END LOOP;
                        return next child_prodlot;
                    END LOOP;
                END LOOP;
            END; $BODY$
        LANGUAGE 'plpgsql';""")

        #creates a function. From int parameter return the stock_move last childs for this paramenter
        cr.execute("""CREATE OR REPLACE FUNCTION block_prodlots_down(integer)
        RETURNS SETOF stock_production_lot AS
        $BODY$
            declare child_move record;
                    parent_prodlot record;
                    result record;
            BEGIN
                 FOR child_move IN select distinct stock_move.* from stock_move
                 inner join stock_move_history_ids on stock_move.id = child_id
                 where prodlot_id = $1 and state != 'cancel'
                 LOOP
                    FOR parent_prodlot IN select distinct stock_production_lot.* from stock_move
                    inner join stock_move_history_ids on parent_id = stock_move.id
                    inner join stock_production_lot on stock_production_lot.id = stock_move.prodlot_id
                    where child_id = child_move.id and stock_move.state != 'cancel' and stock_production_lot.id != $1
                    LOOP
                        FOR result in select distinct * from block_prodlots_down(parent_prodlot.id)
                        LOOP
                            return next result;
                        END LOOP;
                        return next parent_prodlot;
                    END LOOP;
                END LOOP;
            END; $BODY$
        LANGUAGE 'plpgsql';""")

plpgsql_block_prodlots()