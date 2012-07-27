# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
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

"""Creates function for show the traceability simplified"""

from osv import osv

class report_stock_simplified(osv.osv):
    """Creates function for show the traceability simplified"""
    _name = "report.stock.simplified"
    _description = "Creates function for show the traceability simplified"
    _auto = False

    def init(self, cr):
        """creates function when install"""
        #check if exists the language plpgsql in bbdd, if not, is created for can create functions in this language
        cr.execute("select * from pg_language where lanname = 'plpgsql'")
        if not cr.rowcount:
            cr.execute("create language 'plpgsql'")

        #creates a function. From int parameter return the stock_move top parents for this paramenter
        cr.execute("""create or replace function stock_move_parents (integer)
            returns setof valid_stock_moves as '
            declare results record;
                child record;
                temp record;
                temp2 record;
                BEGIN
                  select into results valid_stock_moves.* from valid_stock_moves inner join stock_move_history_ids on valid_stock_moves.id = stock_move_history_ids.parent_id where stock_move_history_ids.child_id = $1;
                  IF found then
                    FOR child IN select valid_stock_moves.id from valid_stock_moves inner join stock_move_history_ids on valid_stock_moves.id = stock_move_history_ids.parent_id where stock_move_history_ids.child_id = $1
                    LOOP
                        FOR temp IN select distinct * from stock_move_parents(child.id)
                        LOOP
                      select into temp2 valid_stock_moves.* from valid_stock_moves inner join stock_move_history_ids on valid_stock_moves.id = stock_move_history_ids.parent_id where stock_move_history_ids.child_id = temp.id;
                      IF not found then
                        return next temp;
                      END IF;
                      CONTINUE;
                        END LOOP;
                    END LOOP;
                  ELSE
                    select into results * from valid_stock_moves where id = $1;
                    return next results;
                  END IF;
                END; '
                language 'plpgsql';""")

        #creates a function. From int parameter return the stock_move last childs for this paramenter
        cr.execute("""create or replace function stock_move_childs (integer)
            returns setof valid_stock_moves as
            $BODY$
            declare results record;
                    parent record;
                    temp record;
                    temp2 record;
                    temp3 record;
            BEGIN
              select into results valid_stock_moves.* from valid_stock_moves inner join stock_move_history_ids on valid_stock_moves.id = stock_move_history_ids.child_id
              where stock_move_history_ids.parent_id = $1;
              IF found then
                FOR parent IN select valid_stock_moves.id from valid_stock_moves inner join stock_move_history_ids on valid_stock_moves.id = stock_move_history_ids.child_id where stock_move_history_ids.parent_id = $1
                LOOP
		    select into temp3 valid_stock_moves.* from valid_stock_moves inner join stock_location on valid_stock_moves.location_dest_id = stock_location.id where valid_stock_moves.id = parent.id and stock_location.usage = 'customer';
		    If found then
			return next temp3;
		    END IF;
                    FOR temp IN select distinct * from stock_move_childs(parent.id)
                    LOOP
			select into temp2 valid_stock_moves.* from valid_stock_moves inner join stock_move_history_ids on valid_stock_moves.id = stock_move_history_ids.child_id where stock_move_history_ids.parent_id = temp.id;
			IF not found then
				return next temp;
			END IF;
                  CONTINUE;
                    END LOOP;
                END LOOP;
              ELSE
                select into results * from valid_stock_moves where id = $1;
                return next results;
              END IF;
            END; $BODY$
            language 'plpgsql';""")

report_stock_simplified()