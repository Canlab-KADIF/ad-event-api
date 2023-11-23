# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

SyMenuMove = Namespace('SyMenuMove')

SyMenuMovePut = SyMenuMove.schema_model('SyMenuMovePut', {

})

@SyMenuMove.route('', methods=['PUT'])
class SyMenuMoveApi(Resource):

	##############################################################
    # PUT
    ##############################################################
	# swagger 파라미터
	swagger = SyMenuMove.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('menuId', type=str, required=True, location='body')
	swagger.add_argument('parentId', type=str, required=True, location='body')
	swagger.add_argument('menuStep', type=int, required=True, location='body')
	swagger.add_argument('menuSort', type=int, required=True, location='body')
	swagger.add_argument('moveType', type=str, required=True, location='body')
	@SyMenuMove.expect(swagger)

	@SyMenuMove.doc(model=SyMenuMovePut)

	def put(self):
		"""
		메뉴 이동
		필수 : Authorization, menuId, parentId, menuStep, menuSort, moveType
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
		parser.add_argument('menuId', type=str, required=True)
		parser.add_argument('parentId', type=str, required=True)
		parser.add_argument('menuStep', type=int, required=True)
		parser.add_argument('menuSort', type=int, required=True)
		parser.add_argument('moveType', type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True
			# if 'pageId' not in parameter or not parameter['pageId']:
			# 	hasParam = False
			if 'menuId' not in parameter or not parameter['menuId']:
				hasParam = False

			if 'parentId' not in parameter or not parameter['parentId']:
				hasParam = False

			if 'menuStep' not in parameter or not parameter['menuStep']:
				hasParam = False

			if 'menuSort' not in parameter or not parameter['menuSort']:
				hasParam = False

			if 'moveType' not in parameter or not parameter['moveType']:
				hasParam = False

			if hasParam :
				menuId = parameter['menuId']
				parentId = parameter['parentId']
				menuStep = parameter['menuStep']
				menuSort = parameter['menuSort']
				moveType = parameter['moveType']

				# 메뉴 위로 이동
				if moveType == 'U':
					# 메뉴 이동 가능 유무 판단
					sql = "SELECT COUNT(*) AS cnt FROM sy_menu WHERE menu_sort < %s " % menuSort
					if menuStep == 1:
						sql = sql + "AND menu_step = 1 "
					else:
						sql = sql + "AND menu_step > 1 AND parent_id = '%s' " % parentId
					cursor.execute(query=sql)
					sortChk = cursor.fetchone()

					if sortChk['cnt'] > 0:
						#  해당 메뉴의 상위메뉴 정보
						sql = """SELECT menu_id, parent_id, menu_step, menu_sort
						FROM sy_menu
						WHERE menu_sort < %s """ % menuSort
						if menuStep == 1:
							sql = sql + "AND menu_step = 1 "
						else:
							sql = sql + "AND menu_step > 1 AND parent_id = '%s' " % parentId

						sql = sql + "ORDER BY menu_sort DESC, menu_id ASC LIMIT 0,1"
						cursor.execute(query=sql)
						prevMenu = cursor.fetchone()

						# 상위메뉴와 현재메뉴의 정렬순서 차이
						moveNum = menuSort - prevMenu['menu_sort']

						# 선택메뉴의 하위메뉴 개수
						sql = """SELECT COUNT(*) AS cnt FROM sy_menu
						WHERE parent_id LIKE '%s%%' OR menu_id = '%s'""" % (menuId[:menuStep*2], menuId)
						cursor.execute(query=sql)
						nextMenu = cursor.fetchone()

						# 상위메뉴를 정렬순서 차이만큼 업데이트
						sql = """UPDATE sy_menu SET menu_sort = menu_sort + %s
						WHERE parent_id LIKE '%s%%' OR menu_id = '%s'  """ % (nextMenu['cnt'], prevMenu['menu_id'][:prevMenu['menu_step']*2], prevMenu['menu_id'])
						cursor.execute(query=sql)

						# 선택메뉴의 정렬순서 값을 업데이트
						sql = """UPDATE sy_menu SET menu_sort = menu_sort - %s
						WHERE parent_id LIKE '%s%%' OR menu_id = '%s' """ % (moveNum, menuId[:menuStep*2], menuId)
						cursor.execute(query=sql)

						# create & update menu json file
						# makeJsonMenu(svt)

					else:
						statusCode = 404
						data['error'] = '해당 단계에서 상위로 이동할 수 없습니다'

				elif moveType == 'D':
					# 메뉴 아래로 이동
					# 메뉴 이동 가능 유무 판단
					sql = "SELECT COUNT(*) AS cnt FROM sy_menu WHERE menu_sort > %s " % menuSort
					if menuStep == 1:
						sql = sql + "AND menu_step = 1 "
					else:
						sql = sql + "AND menu_step > 1 AND parent_id = '%s' " % parentId
					cursor.execute(query=sql)
					sortChk = cursor.fetchone()

					if sortChk['cnt'] > 0:
						# 해당 메뉴의 하위메뉴 정보
						sql = """SELECT menu_id, parent_id, menu_step, menu_sort
						FROM sy_menu
						WHERE menu_sort > %s """ % menuSort
						if menuStep == 1:
							sql = sql + "AND menu_step = 1 "
						else:
							sql = sql + "AND menu_step > 1 AND parent_id = '%s' " % parentId

						sql = sql + "ORDER BY menu_sort, menu_id LIMIT 0,1"
						cursor.execute(query=sql)
						prevMenu = cursor.fetchone()

						# 하위메뉴와 현재메뉴의 정렬순서 차이
						moveNum = prevMenu['menu_sort'] - menuSort

						# 하위메뉴의 개수
						sql = """SELECT COUNT(*) AS cnt FROM sy_menu
						WHERE parent_id LIKE '%s%%' OR menu_id = '%s'""" % (prevMenu['menu_id'][:prevMenu['menu_step']*2], prevMenu['menu_id'])
						cursor.execute(query=sql)
						nextMenu = cursor.fetchone()

						# 하위메뉴를 정렬순서 차이만큼 업데이트
						sql = """UPDATE sy_menu SET menu_sort = menu_sort - %s
						WHERE parent_id LIKE '%s%%' OR menu_id = '%s'  """ % (moveNum, prevMenu['menu_id'][:prevMenu['menu_step']*2], prevMenu['menu_id'])
						cursor.execute(query=sql)

						# 선택메뉴의 정렬순서 값을 업데이트
						sql = """UPDATE sy_menu SET menu_sort = menu_sort + %s
						WHERE parent_id LIKE '%s%%' OR menu_id = '%s' """ % (nextMenu['cnt'], menuId[:menuStep*2], menuId)
						cursor.execute(query=sql)

						# create & update menu json file
						# makeJsonMenu(svt)

					else:
						statusCode = 404
						data['error'] = '해당 단계에서 하위로 이동할 수 없습니다'

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
