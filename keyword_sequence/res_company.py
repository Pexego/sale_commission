

from osv import osv,fields

class res_company(osv.osv):

    _inherit="res.company"
    _columns ={
    'keyword': fields.char('Keyword',size=10)

    }
res_company()