# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from datetime import date
from openerp.exceptions import UserError, ValidationError
import time
import requests
import json
import base64

URL = "https://apirenaper.idear.gov.ar/apidatos"

URL_ROSTRO = "https://apirenaper.idear.gov.ar/"

class ExtendsResPartnerSid(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	# API Datos DNI
	sid_ids = fields.One2many('financiera.sid.datos', 'partner_id', "SID - Datos DNI")
	sid_id = fields.Many2one('financiera.sid.datos', "SID - Datos DNI actual")
	# API Rostro
	sid_rostro_ids = fields.One2many('financiera.sid.rostro', 'partner_id', "SID - Rostro")
	sid_rostro_id = fields.Many2one('financiera.sid.rostro', "SID - Rostro actual")

	@api.one
	def obtener_datos(self, dni, sexo, tramite=None):
		if len(self.company_id.sid_id) > 0:
			self.company_id.sid_id.set_api_datos_token()
			token = self.company_id.sid_id.api_datos_token
			url = URL
			if tramite == None:
				url += "/porDniSexo.php?dni=%s&sexo=%s"%(str(dni),str(sexo))
			else:
				url += "porDniSexoTramite.php?dni=%s&sexo=%s&idtramite=%s"%(str(dni),str(sexo),str(tramite))
			headers = {
				'authorization': "Bearer %s"%token,
			}
			r = requests.get(url, headers=headers)
			data = r.json()
			if data['codigo'] == 99:
				new_sid_id = self.env['financiera.sid.datos'].from_dict(data, self.id)
				self.sid_ids = [new_sid_id.id]
				self.sid_id = new_sid_id.id
		else:
			raise ValidationError("Falta configurar SID. Contacte al administrador!")
	
	@api.one
	def obtener_datos_sid(self):
		dni = self.dni
		if dni == None or dni == False:
			raise ValidationError("Falta cargar DNI del cliente.")
		if self.sexo == False or self.sexo == None:
			raise ValidationError("Falta cargar el sexo del cliente.")
		sexo = self.sexo.upper()[:1]
		self.obtener_datos(dni, sexo)

	# API ROSTRO

	@api.one
	def obtener_rostro(self, imagen, dni, sexo):
		if len(self.company_id.sid_id) > 0:
			self.sid_rostro_id = None
			self.company_id.sid_id.set_api_rostro_token()
			token = self.company_id.sid_id.api_rostro_token
			url = URL_ROSTRO + "CHUTROFINAL/API_ABIS/apiInline_v3.php"
			headers = {
				'authorization': "Bearer %s"%token,
			}
			body = {
				'imagen': imagen,
				'dni': dni,
				'sexo': sexo,
			}
			r = requests.post(url, data=json.dumps(body), headers=headers)
			data = r.json()
			if data['codigo_http'] == 200 and data['data']['codigo'] == 200:
				new_sid_rostro_id = self.env['financiera.sid.rostro'].from_dict(data['data'], self.id)
				self.sid_rostro_ids = [new_sid_rostro_id.id]
				self.sid_rostro_id = new_sid_rostro_id.id
				# Obtener resultado puede demorar hasta 5 segundos o mas luego
				# de la consulta - ver como manejar esto
				i = 1
				while (new_sid_rostro_id.status == False and i <= 10):
					new_sid_rostro_id.obtener_resultado()
					i = i + 1
		else:
			raise ValidationError("Falta configurar SID. Contacte al administrador!")
	
	@api.one
	def obtener_rostro_sid(self):
		imagen = self.app_selfie
		if imagen == None or imagen == False:
			raise ValidationError("Falta cargar la selfie del cliente.")
		dni = self.dni
		if dni == None or dni == False:
			raise ValidationError("Falta cargar DNI del cliente.")
		if self.sexo == False or self.sexo == None:
			raise ValidationError("Falta cargar el sexo del cliente.")
		sexo = self.sexo.upper()[:1]
		self.obtener_rostro(imagen, dni, sexo)

	def set_estado_rostro_sid(self):
		ret = False
		if len(self.sid_rostro_id) > 0:
			if self.sid_rostro_id.status == 'HIT':
				self.confirm()
				self.state = 'validated'
				ret = 'validated'
		else:
			raise ValidationError("No se encontro objeto SID.")
		return ret