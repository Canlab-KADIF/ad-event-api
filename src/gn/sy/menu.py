# -*- coding: utf-8 -*-
import logging
from os import stat
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

SyMenu = Namespace('SyMenu')

SyMenuGet = SyMenu.schema_model('SyMenuGet', {

})
SyMenuPost = SyMenu.schema_model('SyMenuPost', {

})
SyMenuPut = SyMenu.schema_model('SyMenuPut', {

})
SyMenuDelete = SyMenu.schema_model('SyMenuDelete', {

})
@SyMenu.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
class SyMenuApi(Resource):
	####################################################################################################################
    # METHOD : GET
    # write  : 23.03.17
    # writer : chside
    ####################################################################################################################
	swagger = SyMenu.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	@SyMenu.expect(swagger)

	@SyMenu.doc(model=SyMenuGet)

	def get(self):
		"""
		메뉴 리스트
		필수 : Authorization
		일반 :
		"""

		statusCode = 200
		data = {'timestamp': datetime.datetime.now().isoformat()}

		# host 정보
		svt, host, userIp = get_server_type(request)

		# 로그인 정보
		payload = decode_jwt(request.headers)
		if payload is None:
			data['error'] = 'Unauthorized'
			return data, 401

		# 관리자 권한 확인
		if payload['role'] < 5:
			data['error'] = '관리자만 접속 가능합니다.'
			return data, 401

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:

			hasParam = True

			if hasParam :

				sql = """
					SELECT
						*
					FROM
						sy_menu
					WHERE
						menu_step = 1
					ORDER BY
						menu_sort, menu_id ASC
				"""
				cursor.execute(query=sql)

				itemList = []
				for row in cursor.fetchall():
					item={}
					item['menuId'] = row['menu_id']
					item['parentId'] = row['parent_id']
					item['menuStep'] = row['menu_step']
					item['menuSort'] = row['menu_sort']
					item['menuName'] = row['menu_name']
					item['menuType'] = row['menu_type']
					item['menuUrl'] = row['menu_url']
					item['menuIcon'] = row['menu_icon']
					item['menuRole'] = row['menu_role']
					item['used'] = row['used']
					item['menuSub'] = get_sub_menu(row['menu_id'], '1', '', svt)
					# item['insertDate'] = row['insert_date'].strftime("%Y-%m-%d %H:%M")
					itemList.append(item)

				data['menuList'] = itemList
				data['iconList'] = commonCode.iconList
				data['roleList'] = get_common_code_list('010000', '1', svt)
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


	####################################################################################################################
    # METHOD : POST
    # write  : 23.03.17
    # writer : chside
    ####################################################################################################################
	# swagger 파라미터
	swagger = SyMenu.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('menuId',   type=str, required=False, location='body')
	swagger.add_argument('menuName', type=str, required=True,  location='body')
	swagger.add_argument('menuStep', type=int, required=True,  location='body')
	swagger.add_argument('menuUrl',  type=str, required=False, location='body')
	swagger.add_argument('menuIcon', type=str, required=False, location='body')
	swagger.add_argument('menuRole', type=str, required=True,  location='body')
	swagger.add_argument('used', 	 type=str, required=True,  location='body')
	@SyMenu.expect(swagger)

	@SyMenu.doc(model=SyMenuPost)

	def post(self):
		"""
		메뉴정보 등록
		필수 : Authorization, menuName, menuStep, menuYn
		일반 : menuId, menuUrl
		"""
		statusCode = 200
		data = {'timestamp': datetime.datetime.now().isoformat()}

		# host 정보
		svt, host, userIp = get_server_type(request)

		# 로그인 정보
		payload = decode_jwt(request.headers)
		if payload is None:
			data['error'] = 'Unauthorized'
			return data, 401

		# 관리자 권한 확인
		if payload['role'] < 5:
			data['error'] = '관리자만 접속 가능합니다.'
			return data, 401

		# 파라미터 정리
		parser = reqparse.RequestParser()
		parser.add_argument('menuId',   type=str, required=False)
		parser.add_argument('menuName', type=str, required=True)
		parser.add_argument('menuStep', type=int, required=True)
		parser.add_argument('menuUrl',  type=str, required=False)
		parser.add_argument('menuIcon', type=str, required=False)
		parser.add_argument('menuRole', type=str, required=True)
		parser.add_argument('used', 	type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True
			if 'menuName' not in parameter or not parameter['menuName']:
				hasParam = False

			if 'menuStep' not in parameter or not parameter['menuStep']:
				hasParam = False

			if 'menuRole' not in parameter or not parameter['menuRole']:
				hasParam = False

			if 'used' not in parameter or not parameter['used']:
				hasParam = False

			if hasParam :
				# parameter 정리
				menuName = parameter['menuName']
				menuStep = parameter['menuStep']
				menuRole = parameter['menuRole']
				used = parameter['used']

				menuId = ''
				if 'menuId' in parameter and parameter['menuId'] != '':
					menuId = parameter['menuId']

				menuUrl = ''
				if 'menuUrl' in parameter and parameter['menuUrl'] != '':
					menuUrl = parameter['menuUrl']

				menuIcon = ''
				if 'menuIcon' in parameter and parameter['menuIcon'] != '':
					menuIcon = parameter['menuIcon']

				sql = "SELECT max(menu_sort)+1 max_menu_sort FROM sy_menu"
				cursor.execute(query=sql)
				sort = cursor.fetchone()
				menuSort = sort['max_menu_sort']

				if menuId == '':
					# 최상위 메뉴 추가
					sql = """SELECT LPAD(IFNULL(MAX(CONVERT(SUBSTR(menu_id, 1, 2),UNSIGNED)),0)+1, 2, 0) AS max_menu_id
					FROM sy_menu
					WHERE menu_step = %s"""
					cursor.execute(query=sql, args=menuStep)
					result = cursor.fetchone()
					# if result['max_menu_id'] > 99:
					# 	hasProcess = False

					newMenuId = str(result['max_menu_id']) + '0000'
					parentId = newMenuId

				else:
					# 2차 메뉴 추가
					sql = """SELECT LPAD(IFNULL(MAX(CONVERT(SUBSTR(menu_id, 3, 2),UNSIGNED)),0)+1, 2, 0) AS max_menu_id
					FROM sy_menu
					WHERE parent_id = %s and menu_step = %s"""
					cursor.execute(query=sql, args=(menuId, menuStep))
					result = cursor.fetchone()

					newMenuId = menuId[:2] + str(result['max_menu_id']) + '00'
					parentId = menuId

				sql = """
					INSERT INTO sy_menu(menu_id, parent_id, menu_step, menu_sort, menu_name, menu_url, menu_icon, menu_role, used, insert_id, insert_ip) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
				"""
				cursor.execute(query=sql, args=(newMenuId, parentId, menuStep, menuSort, menuName, menuUrl, menuIcon, menuRole, used, payload['userId'], userIp))

				# create & update menu json file
				menuType = 'M'


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


	####################################################################################################################
    # METHOD : PUT
    # write  : 23.03.17
    # writer : chside
    ####################################################################################################################
	# swagger 파라미터
	swagger = SyMenu.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('menuId',   type=str, required=True,  location='body')
	swagger.add_argument('menuName', type=str, required=True,  location='body')
	swagger.add_argument('menuUrl',  type=str, required=False, location='body')
	swagger.add_argument('menuIcon', type=str, required=False, location='body')
	swagger.add_argument('menuRole', type=str, required=False, location='body')
	swagger.add_argument('used',   	 type=str, required=True,  location='body')
	@SyMenu.expect(swagger)

	@SyMenu.doc(model=SyMenuPut)

	def put(self):
		"""
		메뉴정보 수정
		필수 : Authorization, menuId, menuName, used
		일반 : menuUrl
		"""
		statusCode = 200
		data = {'timestamp': datetime.datetime.now().isoformat()}

		# host 정보
		svt, host, userIp = get_server_type(request)

		# 로그인 정보
		payload = decode_jwt(request.headers)
		if payload is None:
			data['error'] = 'Unauthorized'
			return data, 401

		# 관리자 권한 확인
		if payload['role'] < 5:
			data['error'] = '관리자만 접속 가능합니다.'
			return data, 401

		# 파라미터 정리
		parser = reqparse.RequestParser()
		parser.add_argument('menuId',   type=str, required=True)
		parser.add_argument('menuName', type=str, required=True)
		parser.add_argument('menuUrl',  type=str, required=False)
		parser.add_argument('menuIcon', type=str, required=False)
		parser.add_argument('menuRole', type=str, required=False)
		parser.add_argument('used',   	type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True
			# if 'pageId' not in parameter or not parameter['pageId']:
			# 	hasParam = False
			if 'menuId' not in parameter or not parameter['menuId']:
				hasParam = False

			if 'menuName' not in parameter or not parameter['menuName']:
				hasParam = False

			if 'used' not in parameter or not parameter['used']:
				hasParam = False


			if hasParam :
				# parameter 정리
				menuId = parameter['menuId']
				menuName = parameter['menuName']
				used = parameter['used']

				menuUrl = ''
				if 'menuUrl' in parameter and parameter['menuUrl'] != '':
					menuUrl = parameter['menuUrl']

				menuIcon = ''
				if 'menuIcon' in parameter and parameter['menuIcon'] != '':
					menuIcon = parameter['menuIcon']

				menuRole = ''
				if 'menuRole' in parameter and parameter['menuRole'] != '':
					menuRole = parameter['menuRole']

				sql = """
					UPDATE sy_menu SET
						menu_name = %s,
						menu_url = %s,
						menu_icon = %s,
						menu_role = %s,
						used = %s
					WHERE menu_id = %s
				"""
				cursor.execute(query=sql, args=(menuName, menuUrl, menuIcon, menuRole, used, menuId))

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


	####################################################################################################################
    # METHOD : DELETE
    # write  : 23.03.17
    # writer : chside
    ####################################################################################################################
	# swagger 파라미터
	swagger = SyMenu.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('menuId', type=str, required=True, location='body')
	@SyMenu.expect(swagger)

	@SyMenu.doc(model=SyMenuDelete)

	def delete(self):
		"""
		메뉴정보 삭제
		필수 : Authorization, menuId
		일반 :
		"""
		statusCode = 200
		data = {'timestamp': datetime.datetime.now().isoformat()}

		# host 정보
		svt, host, userIp = get_server_type(request)

		# 로그인 정보
		payload = decode_jwt(request.headers)
		if payload is None:
			data['error'] = 'Unauthorized'
			return data, 401

		# 관리자 권한 확인
		if payload['role'] < 5:
			data['error'] = '관리자만 접속 가능합니다.'
			return data, 401

		# 파라미터 정리
		parser = reqparse.RequestParser()
		parser.add_argument('menuId', type=str, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True
			# if 'pageId' not in parameter or not parameter['pageId']:
			# 	hasParam = False
			if 'menuId' not in parameter or not parameter['menuId']:
				hasParam = False

			if hasParam :
				# parameter 정리
				menuId = parameter['menuId']

				sql = """SELECT menu_step, (CASE WHEN menu_step = 1
				THEN (SELECT COUNT(*) FROM sy_menu WHERE menu_step <> 1 AND parent_id = %s)  ELSE 0 END) AS menuSubCount
				FROM sy_menu
				WHERE menu_id = %s"""
				cursor.execute(query=sql, args=(menuId, menuId))
				result = cursor.fetchone()

				if result['menuSubCount'] < 1:
					sql = "DELETE FROM sy_menu WHERE menu_id = %s"
					cursor.execute(query=sql, args=menuId)

				else:
					statusCode = 404
					data['error'] = "하위 메뉴가 존재하여 삭제 할 수 없습니다"


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
