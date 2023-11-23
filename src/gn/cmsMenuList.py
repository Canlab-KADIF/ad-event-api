# -*- coding: utf-8 -*-
import logging
from os import stat
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

GnCmsMenuList = Namespace('GnCmsMenuList')

GnCmsMenuListGet = GnCmsMenuList.schema_model('GnCmsMenuListGet', {

})

@GnCmsMenuList.route('', methods=['GET'])
class GnCmsMenuListApi(Resource):

	swagger = GnCmsMenuList.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('pageId', required=False, location='body', help='로그인토큰')
	@GnCmsMenuList.expect(swagger)

	@GnCmsMenuList.doc(model=GnCmsMenuListGet)

	def get(self):
		"""
		메뉴 리스트
		필수 : Authorization
		일반 : pageId
		"""

		statusCode = 200
		data = {'timestamp': datetime.datetime.now().isoformat()}

		# host 정보
		serverType, host, userIp = get_server_type(request)

		# 로그인 정보
		payload = decode_jwt(request.headers)
		if payload is None:
			data['error'] = 'Unauthorized'
			return data, 401

		# 관리자 권한 확인
		if payload['role'] < 3:
			data['error'] = '권한이 없습니다'
			return data, 401

		# 파라미터 정리
		parser = reqparse.RequestParser()
		parser.add_argument('pageId', type=str, required=False, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(serverType))

		try:

			hasParam = True

			if hasParam :
				pageId = ''
				if parameter['pageId'] is not None:
					pageId = parameter['pageId']

				sql = """
					SELECT
						menu_id, parent_id, menu_step, menu_sort, menu_name, menu_type, menu_url, menu_icon, menu_role
					FROM
						sy_menu sm
					WHERE
						delete_id IS NULL
						AND menu_step = 1
						AND used = 1
						AND menu_role <= %s
					ORDER BY
						menu_sort, menu_id
				"""
				cursor.execute(query=sql, args=payload['role'])

				itemList = []
				for row in cursor.fetchall():
					item={}
					item['active'] = ""
					item['menuId'] = row['menu_id']
					item['parentId'] = row['parent_id']
					item['menuName'] = row['menu_name']
					item['menuStep'] = row['menu_step']
					item['menuSort'] = row['menu_sort']
					item['menuType'] = row['menu_type']
					item['menuUrl'] = row['menu_url']
					item['menuIcon'] = row['menu_icon']
					item['menuRole'] = row['menu_role']
					# 2차 메뉴
					item['menuSub'] = get_sub_menu(row['menu_id'], '1', payload['role'], serverType)

					itemList.append(item)

				data['menuList'] = itemList

			else:
				statusCode = 404
				data['error'] = 'No Parameter'

		except Exception as e :
			logging.error(traceback.format_exc())
			data['error'] = 'exception error'
			statusCode = 505
			return data, statusCode

		finally:
			cursor.close()

		return json_null_to_empty(data),statusCode





