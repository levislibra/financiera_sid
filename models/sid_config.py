# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.exceptions import UserError, ValidationError
import logging

import requests
import json

_logger = logging.getLogger(__name__)

URL_API_DATOS = "http://150.136.1.69:8011/CHUTROFINAL/API_ABIS/Autorizacion/token.php"

class FinancieraSidConfig(models.Model):
	_name = 'financiera.sid.config'

	name = fields.Char("Nombre")
	# Api Datos
	api_datos_usuario = fields.Char("Usuario")
	api_datos_clave = fields.Char("Clave")
	api_datos_token = fields.Char("Token")
	# Api Rostro
	api_rostro_usuario = fields.Char("Usuario")
	api_rostro_clave = fields.Char("Clave")
	api_rostro_token = fields.Char("Token")
	company_id = fields.Many2one('res.company', 'Empresa')

	@api.one
	def set_api_datos_token(self):
		body = {
			'username': self.api_datos_usuario,
			'password': self.api_datos_clave,
		}
		r = requests.post(URL_API_DATOS, data=body)
		data = r.json()
		if 'data' in data and data['data']['codigo'] == 0:
			self.api_datos_token = data['data']['token']
		elif 'data' in data:
			raise UserError(data['data']['mensaje'])

	@api.one
	def set_api_rostro_token(self):
		body = {
			'username': self.api_rostro_usuario,
			'password': self.api_rostro_clave,
		}
		r = requests.post(URL_API_DATOS, data=body)
		data = r.json()
		if 'data' in data and data['data']['codigo'] == 0:
			self.api_rostro_token = data['data']['token']
		elif 'data' in data:
			raise UserError(data['data']['mensaje'])
