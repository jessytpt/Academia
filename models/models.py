# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions, _
import time 
from psycopg2 import IntegrityError
from datetime import timedelta
   
def get_uid(self, *a):
#si se desea ver que nomas tiene la variable usar pdb
#    import pdb; pdb.set_trace()
    return self.env.uid

class Course(models.Model):
     _name = 'openacademy.course'

     name = fields.Char(string="Title", required=True)
     description = fields.Text()
#     responsible_id = fields.Many2one('res.users', string="Responsible",
#			index=True, ondelete='set null')
#lamdba self, a*:self.env.uid toma por defecto el usuario por defecto
     responsible_id = fields.Many2one(
     'res.users', string="Responsible",
     index=True, ondelete='set null', 
     #default=lambda self, *a: self.env.uid)
     default=get_uid)
     session_ids = fields.One2many('openacademy.session', 'course_id')

#tambén se pueden usar los contrains de postgresql
#para ello es necesario declarar l variable reservada _sql_contrains
     _sql_constraints = [
         ('name_description_check',
          'CHECK( name != description)',
          "The title of the course should not be the same description"),
         ('name_unique',
          'UNIQUE(name)',
          "The course title must be unique",
         ),             
     ]

#ESTA MANERA SÓLO FUNCIONA VEZ
#PORQUE ESTÁ CONCATENADO ' otro' por tanto la segunda vez será un registro duplicado
     def copy(self, default=None):
         if default is None:
             default = {} 
#       entonces utiliza un dicionario vació
#PARA SOLUCIONAR LA DUCLICIDAD AL COPIAR aumentar copied_count
         copied_count = self.search_count([('name', 'ilike', _('Copy of %s%%') %(self.name))])
         if not copied_count:
            new_name = _("Copy of %s") % (self.name)
         else:
            new_name = _("Copy of %s (%s)")% (self.name, copied_count)
#primero contamos cuantos existen con ese nombre
# % en Python es para concatenar
# % en posgres es cualquier cosa similar a (lo que esté antes)
#         default['name'] = self.name + ' otro'    # se reemplaza por
         default['name'] = new_name
# para visualizar la excepcion que me devuelve a l duplicar un dato se usa pdb
#         import pdb; pdb.set_trace()
#         try:
         return super(Course, self).copy(default)
#         except IntegrityError:
#             import pdb; pdb.set_trace()
            # print e
#       return super(NombreClasePython, self).copy(nombreParámetro)
#       pero cómo se q puedo acceder al método .copy
#       por que model hereda de la clase Model que está en el repositorio local de odoo
#      (models.Model)
#       si redefino el método original, con el super mando a llamar el método 
#       pero cambiando el compartamiento particular, en este caso es
#       concatenando ' otro'

class Session(models.Model):
     _name = 'openacademy.session'

     name = fields.Char(required=True)
# fields.Data declara un campo de tipo fecha y desplega un calendario
#     start_date = fields.Date()
# default=fields.Date.today -> por defecto muestra la fecha actual
     start_date = fields.Date(default=fields.Date.today)
# lambda *a: quiere decir que se le puede pasar cualquier parametro 
#y lo procesará, sin embargo esta es una manera muy técnica
#     datetime_test = fields.Datetime(default=lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'))
# odoo tiene su propia manera para que no nos compliquemos
     datetime_test = fields.Datetime(default=fields.Datetime.now)
     duration = fields.Float(digits=(6, 2), help="Duration in days")
     seats = fields.Integer(string="Number of seats")
     instructor_id = fields.Many2one('res.partner', string='Instructor'
     , domain=['|', ('instructor', '=', True),
     ('category_id.name', 'ilike', 'Teacher')])
     course_id = fields.Many2one('openacademy.course', ondelete='cascade',
     string="Course", required=True)
     
     attendee_ids = fields.Many2many('res.partner', string="Attendees")
#   taken_seats es un campo calculado que no existe en la base de datos 
#   para  que se agregue a la base de datos se le aumenta el parámetro store=True
     taken_seats = fields.Float(compute='_taken_seats', store=True)
#   campo reservado active, siempre debe ser decclarado como boolean
#   por defecto será true, es decir que al crear una sesión estará activa
     active = fields.Boolean(default=True)
#     end_date = fields.Date(store=True, compute='_get_end_date')
#   la línea anterior no permitíacapturar el valor del campo, sólo lo visualizaba
#   para poder calcularlo se usa el concepto inverse, que se ve acontinuación 
     end_date = fields.Date(store=True, compute='_get_end_date',
                            inverse='_set_end_date')
     attendees_count = fields.Integer(compute='_get_attendees_count', store=True)
     color = fields.Float() 
     hours = fields.Float(
              string="Duration in hours",
              compute='_get_hours', inverse='_set_hours')
     
     @api.depends('duration')
     def _get_hours(self):
         for r in self:
             r.hours = r.duration * 24
     
     def _set_hours(self):
         for r in self:
             r.duration = r.horus / 24

     @api.depends('attendee_ids')
     def _get_attendees_count(self):
         for record in self:
             record.attendees_count = attendees_count = len(record.attendee_ids)

     @api.depends('start_date', 'duration')
     def _get_end_date(self):
#         import pdb;pdb.set_trace()
         for record in self.filtered('start_date'):
             start_date = fields.Datetime.from_string(record.start_date)
             record.end_date = start_date + timedelta(days=record.duration, seconds=-1)

     def _set_end_date(self):
          for record in self.filtered('start_date'):
              start_date = fields.Datetime.from_string(record.start_date)
              end_date = fields.Datetime.from_string(record.end_date)
              record.duration = (end_date - start_date).days + 1

     @api.depends('seats', 'attendee_ids')
     def _taken_seats(self):
#         import pdb;pdb.set_trace()
#        for record in self:
#            if not record.seats: record.taken_seats = 0.0  
#            else: record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats
         for record in self.filtered(lambda r: r.seats):
             record.taken_seats = 100.0 * len(record.attendee_ids) / record.seats

     @api.onchange('seats', 'attendee_ids')
     def _verify_valid_seats(self):
#         if self.seats < 0:
         if self.filtered(lambda r: r.seats < 0):
             self.active = False
             return {
                'warning': {
                    'title': _("Incorrect 'seats' value"),
                    'message': _("The number of available seats may not be negative"),      
                            }
                    }
         if self.seats < len(self.attendee_ids):
             self.active = False
             return{
                 'warning':{
                     'title': _("Too many attendees"),
                     'message': _("Increase seats or remove excess attendess"),
                           }
                    }
         self.active = True

     @api.constrains('instructor_id', 'attendee_ids')
     def _check_instructor_not_in_attendees(self):
          for record in self.filtered('instructor_id'):
              if record.instructor_id in record.attendee_ids:
                  raise exceptions.ValidationError(
				_("A session's instructor can't be an attendee"))
