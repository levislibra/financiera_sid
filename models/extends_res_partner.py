# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import relativedelta
from datetime import date
from openerp.exceptions import UserError, ValidationError
import time
import requests
import json
import sid_request_data

URL = "https://apirenaper.idear.gov.ar/apidatos"

class ExtendsResPartnerSid(models.Model):
	_name = 'res.partner'
	_inherit = 'res.partner'

	sid_ids = fields.One2many('financiera.sid.datos', 'partner_id', "SID - Datos DNI")
	sid_id = fields.Many2one('financiera.sid.datos', "SID - Datos DNI actual")

	@api.one
	def obtener_datos_sid(self, dni, sexo, tramite=None):
		if len(self.company_id.sid_id) > 0:
			token = self.company_id.sid_id.api_datos_token
			url = URL
			if tramite == None:
				url += "/porDniSexo.php?dni=%s&sexo=%s"%(str(dni),str(sexo))
			headers = {
				'authorization': "Bearer %s"%token,
			}
			r = requests.get(url, headers=headers)
			data = r.json()
			print("data: ", data)
			new_sid_id = self.env['financiera.sid.datos'].from_dict(data, self.id)
			self.sid_ids = [new_sid_id.id]
			if new_sid_id.codigo == 0:
				self.sid_id = new_sid_id.id
		else:
			raise ValidationError("Falta configurar SID. Contacte al administrador!")
	
	@api.one
	def button_obtener_datos_sid(self):
		dni = self.dni
		if dni == None or dni == False:
			raise ValidationError("Falta cargar DNI del cliente.")
		if self.sexo == False or self.sexo == None:
			raise ValidationError("Falta cargar el sexo del cliente.")
		sexo = self.sexo.upper()[:1]
		self.obtener_datos_sid(dni, sexo)