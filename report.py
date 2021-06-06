# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, models
#from odoo import api, models

class ReportSession(models.AbstractModel):
    _name = "report.openacademy.report_session"

#    @api.model
#    def render_html(self, docids, data=None):
#        data = self.env[].get_report_data(docids)
#        docargs = {
#            'doc_ids': self.ids,
#            'doc_model': self.model,
#            'data': 'hola',
#        }
#        return self.env['report'].render('openacademy.report_session',docargs)

#----------------
#    @api.model
#    def render_hrml(self, docids, data=None):
#          docargs = {
#            'doc_ids': self.ids,
#            'doc_model': self.model,
#            'data': 'hola',
#          }
#          return self.env['report'].render("openacademy.report_session", docargs)
#----------    
    @api.model
    def _get_report_values(self, docids, data=None):
         docs = self.env['openacademy.session'].browse(docids)
         return {
              'doc_ids': docids,
              'doc_model': 'report.model',
              'docs': docs,
              'lines': self.some_func(docs),
              'data': 'Hola',
         }
#------------
#    _name = "report.openacademy.report_session_view" _description = "Report Name"

#    @api.multi 
#    def render_html(self, data=None): 
##    def render_html(self, docids, data=None):
#        report_obj = self.env["report"]
#        report = report_obj._get_report_from_name("openacademy.report_session")
#        docargs = {
#            "doc_ids": self._ids,
#            "doc_ids": docids,
#	    "doc_model": report.model,
#            "docs": self,
# 	    "docs": self.env['openacademy.session'].browse(docids),            
#	    "other_variable": 'other value',
#        }
#        return report_obj.render("openacademy.report_session", docargs)
#        return report_obj.render("openacademy.report_session_view", docargs)


