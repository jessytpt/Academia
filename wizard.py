# _*_ coding utf-8 -*-

from odoo import models, fields, api

class Wizard(models.TransientModel):
    _name = 'openacademy.wizard'

# método para llenar por defecto, el nombre de session 
    def _default_session(self):
        return self.env['openacademy.session'].browse(self._context.get('active_ids'))

    session_ids = fields.Many2many(
             'openacademy.session',required=True,default=_default_session)
    attendee_ids = fields.Many2many('res.partner')
 
    @api.multi
    def subscribe(self):
#        self.session_id.attendee_ids |= self.attendee_ids
        for session in self.session_ids:
            session.attendee_ids |= self.attendee_ids
        return {} 
