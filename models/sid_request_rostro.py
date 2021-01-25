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

class SidRostro(models.Model):
	_name = 'financiera.sid.rostro'
	
	_order = 'id desc'
	name = fields.Char("Nombre para mostrar")
	partner_id = fields.Many2one('res.partner', 'Cliente')
	codigo = fields.Integer("Codigo")
	mensaje = fields.Char("Mensaje")
	# Notificacion
	transaction_control_number = fields.Char("Numero de control de transaccion")
	type_of_transaction = fields.Char("Tipo de transaccion")
	date_of_transaction = fields.Char("Fecha de transaccion")
	# Resultado
	tcn = fields.Char("TCN")
	status = fields.Char("Estado")
	score = fields.Char("Score")
	matchtype = fields.Char("Tipo de comprobacion")
	comments = fields.Char("Comentarios")
	fechanoti = fields.Char("Fecha resultado")
	horanoti = fields.Char("Hora resultado")
	company_id = fields.Many2one('res.company', 'Empresa', related='partner_id.company_id', readonly=True)

	@api.model
	def create(self, values):
		rec = super(SidRostro, self).create(values)
		rec.update({
			'name': 'SID/ROSTRO/' + str(rec.id).zfill(8),
		})
		return rec

	@api.model
	def from_dict(self, obj, partner_id):
		ret = False
		if isinstance(obj, dict):
			values = {
				'partner_id': partner_id,
				'codigo': from_int(obj.get(u"codigo")),
				'mensaje': from_str(obj.get(u"mensaje")),
				'transaction_control_number': from_str(obj.get(u"notificacion").get(u"transactionControlNumber")),
				'type_of_transaction': from_str(obj.get(u"notificacion").get(u"typeOfTransaction")),
				'date_of_transaction': from_str(obj.get(u"notificacion").get(u"dateOfTransaction")),
			}
			ret = self.env['financiera.sid.rostro'].create(values)
		return ret

	@api.one
	def from_dict_result(self, obj):
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
			self.update(values)

	@api.one
	def obtener_resultado(self):
		if self.transaction_control_number:
			token = self.company_id.sid_id.api_datos_token
			url = URL_ROSTRO + "/CHUTROFINAL/API_ABIS/resultadoTCN.php?id=%s"%self.transaction_control_number
			headers = {
				'authorization': "Bearer %s"%token,
			}
			r = requests.get(url, headers=headers)
			data = r.json()
			if data['codigo_http'] == 200 and data['data']['codigo'] == 0:
				self.from_dict_result(data['data']['notificacion'])
				self.resultado_id = self.id
			elif data['codigo_http'] == 200 and data['data']['codigo'] == 1:
				self.company_id.sid_id.set_api_rostro_token()
				return self.obtener_resultado()
			else:
				raise ValidationError(data['data']['mensaje'])
		else:
			raise ValidationError("Falta el TCN.")
