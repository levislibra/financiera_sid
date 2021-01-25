# coding: utf-8

# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = sid_rostro_from_dict(json.loads(json_string))
from openerp import models, fields, api
from datetime import datetime, timedelta, date
from dateutil import relativedelta
from openerp.exceptions import UserError, ValidationError
from enum import Enum
import dateutil.parser
import requests

URL_ROSTRO = "https://apirenaper.idear.gov.ar/"

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

def from_list(f, x):
	assert isinstance(x, list)
	return [f(y) for y in x]

def to_class(c, x):
	assert isinstance(x, c)
	return x.to_dict()

# class SidRostroErrorArray(models.Model):
# 	_name = "financiera.sid.rostro.errorarray"

# 	code = fields.Char("Codigo")
# 	description = fields.Char("Descripcion")
# 	name = fields.Char("Nombre")

# 	@api.model
# 	def from_dict(self, obj):
# 		ret = False
# 		if isinstance(obj, dict):
# 			values = {
# 				'code': from_str(obj.get(u"code")),
# 				'description': from_str(obj.get(u"description")),
# 				'name': from_str(obj.get(u"name")),
# 			}
# 			ret = self.env['financiera.sid.rostro.errorarray'].create(values).id
# 		return ret

# class SidNotificacion(models.Model):
# 	_name = 'financiera.sid.rostro.notificacion'
	
# 	transaction_control_number = fields.Char("Numero de control de transaccion")
# 	type_of_transaction = fields.Char("Tipo de transaccion")
# 	date_of_transaction = fields.Char("Fecha de transaccion")
# 	error_array = fields.Many2one('financiera.sid.rostro.errorarray')

# 	@api.model
# 	def from_dict(self, obj):
# 		ret = False
# 		if isinstance(obj, dict):
# 			values = {
# 				'transaction_control_number': from_str(obj.get(u"transactionControlNumber")),
# 				'type_of_transaction': from_str(obj.get(u"typeOfTransaction")),
# 				'date_of_transaction': from_str(obj.get(u"dateOfTransaction")),
# 				'error_array': self.env['financiera.sid.rostro.errorarray'].from_dict(obj.get(u"errorArray")),
# 			}
# 			ret = self.env['financiera.sid.rostro.notificacion'].create(values).id
# 		return ret

class SidRostro(models.Model):
	_name = 'financiera.sid.rostro'
	
	_order = 'id desc'
	partner_id = fields.Many2one('res.partner', 'Cliente')
	codigo = fields.Integer("Codigo")
	mensaje = fields.Char("Mensaje")
	
	# notificacion_id = fields.Many2one('financiera.sid.rostro.notificacion', 'Solicitud')
	transaction_control_number = fields.Char("Numero de control de transaccion")
	type_of_transaction = fields.Char("Tipo de transaccion")
	date_of_transaction = fields.Char("Fecha de transaccion")
	# errores
	# error_code = fields.Char("Codigo")
	# error_description = fields.Char("Descripcion")
	# error_name = fields.Char("Nombre")

	resultado_id = fields.Many2one('financiera.sid.rostro.resultado', 'Resultado')
	company_id = fields.Many2one('res.company', 'Empresa', related='partner_id.company_id', readonly=True)

	@api.model
	def from_dict(self, obj, partner_id):
		ret = False
		if isinstance(obj, dict):
			values = {
				'partner_id': partner_id,
				'codigo': from_int(obj.get(u"codigo")),
				'mensaje': from_str(obj.get(u"mensaje")),

				# 'notificacion_id': self.env['financiera.sid.rostro.notificacion'].from_dict(obj.get(u"notificacion")),
				'transaction_control_number': from_str(obj.get(u"notificacion").get(u"transactionControlNumber")),
				'type_of_transaction': from_str(obj.get(u"notificacion").get(u"typeOfTransaction")),
				'date_of_transaction': from_str(obj.get(u"notificacion").get(u"dateOfTransaction")),
				# obj.get(u"errorArray")
				# 'error_code': from_str(obj.get(u"notificacion").get(u"errorArray").get(u"code")),
				# 'error_description': from_str(obj.get(u"notificacion").get(u"errorArray").get(u"description")),
				# 'error_name': from_str(obj.get(u"notificacion").get(u"errorArray").get(u"name")),
			}
			ret = self.env['financiera.sid.rostro'].create(values)
		return ret
	
	@api.one
	def obtener_resultado(self):
		if len(self.notificacion_id) > 0 and self.notificacion_id.transaction_control_number:
			token = self.company_id.sid_id.api_datos_token
			url = URL_ROSTRO + "/CHUTROFINAL/API_ABIS/resultadoTCN.php?id=%s"%self.notificacion_id.transaction_control_number
			headers = {
				'authorization': "Bearer %s"%token,
			}
			r = requests.get(url, headers=headers)
			data = r.json()
			print("obtener_resultado:data: ", data)
			if data['codigo_http'] == 200 and data['data']['codigo'] == 0:
				new_sid_rostro_resultado_id = self.env['financiera.sid.rostro.resultado'].from_dict(data['data'])
				print("new_sid_rostro_resultado_id: ", new_sid_rostro_resultado_id)
				self.resultado_id = new_sid_rostro_resultado_id.id
			elif data['codigo_http'] == 200 and data['data']['codigo'] == 1:
				self.company_id.sid_id.set_api_rostro_token()
				return self.obtener_resultado()
			else:
				raise ValidationError(data['data']['mensaje'])

# Resultado Sid Rostro *****************************************************

class SidRostroResultadoNotificacion(models.Model):
	_name = 'financiera.sid.rostro.resultado.notificacion'
	
	tcn = fields.Char("TCN")
	status = fields.Char("Estado")
	score = fields.Char("Score")
	matchtype = fields.Char("Tipo de comprobacion")
	comments = fields.Char("Comentarios")
	fechanoti = fields.Char("Fecha resultado")
	horanoti = fields.Char("Hora resultado")

	@api.model
	def from_dict(self, obj):
		ret = False
		if isinstance(obj, dict):
			values = {
				'tcn': from_str(obj.get(u"TCN")),
				'status': from_str(obj.get(u"status")),
				'score': from_str(obj.get(u"score")),
				'matchtype': from_str(obj.get(u"matchtype")),
				'comments': from_str(obj.get(u"comments")),
				'fechanoti': from_str(obj.get(u"fechanoti")),
				'horanoti': from_str(obj.get(u"horanoti")),
			}
			ret = self.env['financiera.sid.rostro.resultado.notificacion'].create(values).id
		return ret

class SidRostroResultado(models.Model):
	_name = 'financiera.sid.rostro.resultado'
	
	notificacion = fields.Many2one('financiera.sid.rostro.resultado.notificacion', "Notificacion")
	codigo = fields.Integer('Codgio')
	mensaje = fields.Char("Mensaje")

	@api.model
	def from_dict(self, obj):
		ret = False
		if isinstance(obj, dict):
			values = {
				'notificacion': self.env['financiera.sid.rostro.resultado.notificacion'].from_dict(obj.get(u"notificacion")),
				'codigo': from_int(obj.get(u"codigo")),
				'mensaje': from_str(obj.get(u"mensaje")),
			}
			ret = self.env['financiera.sid.rostro.resultado'].create(values)
		return ret
