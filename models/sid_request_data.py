# coding: utf-8

# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = welcome_from_dict(json.loads(json_string))
from openerp import models, fields, api
from datetime import datetime, timedelta, date
from dateutil import relativedelta
from openerp.exceptions import UserError, ValidationError
from enum import Enum
import dateutil.parser

def from_str(x):
	ret = ""
	if isinstance(x, (str, unicode)):
		ret = x
	return ret

def from_int(x):
    assert isinstance(x, int) and not isinstance(x, bool)
    return x

def from_datetime(x):
	if not x or x == "":
		ret = False
	else:
		ret = dateutil.parser.parse(x)
	return ret

def to_class(c, x):
    assert isinstance(x, c)
    return x.to_dict()

class SidDatos(models.Model):
	_name = 'financiera.sid.datos'
	
	_order = "id desc"
	name = fields.Char('Nombre para mostrar')	
	partner_id = fields.Many2one("res.partner", "Cliente")
	id_tramite_principal = fields.Char("Id tramite principal")
	id_tramite_tarjeta_reimpresa = fields.Integer("Id tramite tarjeta reimpresa")
	ejemplar = fields.Char("Ejemplar")
	vencimiento = fields.Date("Vencimiento")
	emision = fields.Date("Emision")
	apellido = fields.Char("Apellido")
	nombres = fields.Char("Nombres")
	fecha_nacimiento = fields.Date("Fecha nacimiento")
	cuil = fields.Char("CUIT")
	calle = fields.Char("Calle")
	numero = fields.Char("Numero")
	piso = fields.Char("Piso")
	departamento = fields.Char("Departamento")
	codigo_postal = fields.Char("Codigo postal")
	barrio = fields.Char("Barrio")
	monoblock = fields.Char("Monoblock")
	ciudad = fields.Char("Ciudad")
	municipio = fields.Char("Municipio")
	provincia = fields.Char("Provincia")
	pais = fields.Char("Pais")
	codigo_fallecido = fields.Integer("Codigo fallecido")
	mensaje_fallecido = fields.Char("Mensaje fallecido")
	id_ciudadano = fields.Char("Id ciudadano")
	codigo = fields.Integer("Codigo")
	mensaje = fields.Char("Mensaje")
	company_id = fields.Many2one('res.company', 'Empresa', related='partner_id.company_id', readonly=True)

	@api.model
	def create(self, values):
		rec = super(SidDatos, self).create(values)
		rec.update({
			'name': 'SID/DNI/' + str(rec.id).zfill(8),
		})
		return rec

	@api.model
	def from_dict(self, obj, partner_id):
		print("SidDatos:from_dict")
		print("self: ", self)
		print("partner_id: ", partner_id)
		rec = False
		if isinstance(obj, dict):
			values = {
				'id_tramite_principal': from_str(obj.get(u"id_tramite_principal")),
				'id_tramite_tarjeta_reimpresa': int(obj.get(u"id_tramite_tarjeta_reimpresa")),
				'ejemplar': from_str(obj.get(u"ejemplar")),
				'vencimiento': from_datetime(obj.get(u"vencimiento")),
				'emision': from_datetime(obj.get(u"emision")),
				'apellido': from_str(obj.get(u"apellido")),
				'nombres': from_str(obj.get(u"nombres")),
				'fecha_nacimiento': from_datetime(obj.get(u"fecha_nacimiento")),
				'cuil': from_str(obj.get(u"cuil")),
				'calle': from_str(obj.get(u"calle")),
				'numero': from_str(obj.get(u"numero")),
				'piso': from_str(obj.get(u"piso")),
				'departamento': from_str(obj.get(u"departamento")),
				'codigo_postal': from_str(obj.get(u"codigo_postal")),
				'barrio': from_str(obj.get(u"barrio")),
				'monoblock': from_str(obj.get(u"monoblock")),
				'ciudad': from_str(obj.get(u"ciudad")),
				'municipio': from_str(obj.get(u"municipio")),
				'provincia': from_str(obj.get(u"provincia")),
				'pais': from_str(obj.get(u"pais")),
				'codigo_fallecido': from_int(obj.get(u"codigo_fallecido")),
				'mensaje_fallecido': from_str(obj.get(u"mensaje_fallecido")),
				'id_ciudadano': from_str(obj.get(u"id_ciudadano")),
				'codigo': from_int(obj.get(u"codigo")),
				'mensaje': from_str(obj.get(u"mensaje")),
				'partner_id': partner_id,
			}
			rec = self.env['financiera.sid.datos'].create(values)
		return rec
