# -*- coding: utf-8 -*-
import logging
from os import stat
import traceback
from unittest import result
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

SyCommonMove = Namespace('SyCommonMove')

SyCommonMovePut = SyCommonMove.schema_model('SyCommonMovePut', {

})

@SyCommonMove.route('', methods=['PUT'])
class SyCommonMoveApi(Resource):

	##############################################################
    # PUT
    ##############################################################
	# swagger 파라미터
	swagger = SyCommonMove.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('codeId', type=str, required=True, location='body')
	swagger.add_argument('parentId', type=str, required=True, location='body')
	swagger.add_argument('codeStep', type=int, required=True, location='body')
	swagger.add_argument('codeSort', type=int, required=True, location='body')
	swagger.add_argument('moveType', type=str, required=True, location='body')
	@SyCommonMove.expect(swagger)

	@SyCommonMove.doc(model=SyCommonMovePut)

	def put(self):
		"""
		메뉴 이동
		필수 : Authorization, codeId, parentId, codeStep, codeSort, moveType
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
		parser.add_argument('codeId', type=str, required=True)
		parser.add_argument('parentId', type=str, required=True)
		parser.add_argument('codeStep', type=int, required=True)
		parser.add_argument('codeSort', type=int, required=True)
		parser.add_argument('moveType', type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True
			# if 'pageId' not in parameter or not parameter['pageId']:
			# 	hasParam = False
			if 'codeId' not in parameter or not parameter['codeId']:
				hasParam = False

			if 'parentId' not in parameter or not parameter['parentId']:
				hasParam = False

			if 'codeStep' not in parameter or not parameter['codeStep']:
				hasParam = False

			if 'codeSort' not in parameter or not parameter['codeSort']:
				hasParam = False

			if 'moveType' not in parameter or not parameter['moveType']:
				hasParam = False

			if hasParam :
				codeId = parameter['codeId']
				parentId = parameter['parentId']
				codeStep = parameter['codeStep']
				codeSort = parameter['codeSort']
				moveType = parameter['moveType']

				# 메뉴 위로 이동
				if moveType == 'U':
					# 메뉴 이동 가능 유무 판단
					sql = "SELECT COUNT(*) AS cnt FROM sy_common WHERE code_sort < %s " % codeSort
					if codeStep == 1:
						sql = sql + "AND code_step = 1 "
					else:
						sql = sql + "AND code_step > 1 AND parent_id = '%s' " % parentId
					cursor.execute(query=sql)
					sortChk = cursor.fetchone()

					if sortChk['cnt'] > 0:
						#  해당 메뉴의 상위메뉴 정보
						sql = """SELECT code_id, parent_id, code_step, code_sort
						FROM sy_common
						WHERE code_sort < %s """ % codeSort
						if codeStep == 1:
							sql = sql + "AND code_step = 1 "
						else:
							sql = sql + "AND code_step > 1 AND parent_id = '%s' " % parentId

						sql = sql + "ORDER BY code_sort DESC, code_id ASC LIMIT 0,1"
						cursor.execute(query=sql)
						prevMenu = cursor.fetchone()

						# 상위메뉴와 현재메뉴의 정렬순서 차이
						moveNum = codeSort - prevMenu['code_sort']

						# 선택메뉴의 하위메뉴 개수
						sql = """SELECT COUNT(*) AS cnt FROM sy_common
						WHERE parent_id LIKE '%s%%' OR code_id = '%s'""" % (codeId[:codeStep*2], codeId)
						cursor.execute(query=sql)
						nextMenu = cursor.fetchone()

						# 상위메뉴를 정렬순서 차이만큼 업데이트
						sql = """UPDATE sy_common SET code_sort = code_sort + %s
						WHERE parent_id LIKE '%s%%' OR code_id = '%s'  """ % (nextMenu['cnt'], prevMenu['code_id'][:prevMenu['code_step']*2], prevMenu['code_id'])
						cursor.execute(query=sql)

						# 선택메뉴의 정렬순서 값을 업데이트
						sql = """UPDATE sy_common SET code_sort = code_sort - %s
						WHERE parent_id LIKE '%s%%' OR code_id = '%s' """ % (moveNum, codeId[:codeStep*2], codeId)
						cursor.execute(query=sql)

					else:
						statusCode = 404
						data['error'] = '해당 단계에서 상위로 이동할 수 없습니다'

				elif moveType == 'D':
					# 메뉴 아래로 이동
					# 메뉴 이동 가능 유무 판단
					sql = "SELECT COUNT(*) AS cnt FROM sy_common WHERE code_sort > %s " % codeSort
					if codeStep == 1:
						sql = sql + "AND code_step = 1 "
					else:
						sql = sql + "AND code_step > 1 AND parent_id = '%s' " % parentId
					cursor.execute(query=sql)
					sortChk = cursor.fetchone()

					if sortChk['cnt'] > 0:
						# 해당 메뉴의 하위메뉴 정보
						sql = """SELECT code_id, parent_id, code_step, code_sort
						FROM sy_common
						WHERE code_sort > %s """ % codeSort
						if codeStep == 1:
							sql = sql + "AND code_step = 1 "
						else:
							sql = sql + "AND code_step > 1 AND parent_id = '%s' " % parentId

						sql = sql + "ORDER BY code_sort, code_id LIMIT 0,1"
						cursor.execute(query=sql)
						prevMenu = cursor.fetchone()

						# 하위메뉴와 현재메뉴의 정렬순서 차이
						moveNum = prevMenu['code_sort'] - codeSort

						# 하위메뉴의 개수
						sql = """SELECT COUNT(*) AS cnt FROM sy_common
						WHERE parent_id LIKE '%s%%' OR code_id = '%s'""" % (prevMenu['code_id'][:prevMenu['code_step']*2], prevMenu['code_id'])
						cursor.execute(query=sql)
						nextMenu = cursor.fetchone()

						# 하위메뉴를 정렬순서 차이만큼 업데이트
						sql = """UPDATE sy_common SET code_sort = code_sort - %s
						WHERE parent_id LIKE '%s%%' OR code_id = '%s'  """ % (moveNum, prevMenu['code_id'][:prevMenu['code_step']*2], prevMenu['code_id'])
						cursor.execute(query=sql)

						# 선택메뉴의 정렬순서 값을 업데이트
						sql = """UPDATE sy_common SET code_sort = code_sort + %s
						WHERE parent_id LIKE '%s%%' OR code_id = '%s' """ % (nextMenu['cnt'], codeId[:codeStep*2], codeId)
						cursor.execute(query=sql)

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
