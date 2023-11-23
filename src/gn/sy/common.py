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

SyCommon = Namespace('SyCommon')

SyCommonGet = SyCommon.schema_model('SyCommonGet', {

})
SyCommonPost = SyCommon.schema_model('SyCommonPost', {

})
SyCommonPut = SyCommon.schema_model('SyCommonPut', {

})
SyCommonDelete = SyCommon.schema_model('SyCommonDelete', {

})
@SyCommon.route('', methods=['GET', 'POST', 'PUT', 'DELETE'])
class SyCommonApi(Resource):
	##############################################################
    # GET
    ##############################################################
	swagger = SyCommon.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	@SyCommon.expect(swagger)

	@SyCommon.doc(model=SyCommonGet)

	def get(self):
		"""
		공통코드 리스트
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
					code_id
					, parent_id
					, code_name
					, code_value
					, code_step
					, code_sort
					, used
				FROM
					sy_common
				WHERE
					code_step = 1
				ORDER BY
					code_sort, code_id
				"""
				cursor.execute(query=sql)

				itemList = []
				for row in cursor.fetchall():
					item={}
					item['codeId'] = row['code_id']
					item['parentId'] = row['parent_id']
					item['codeName'] = row['code_name']
					item['codeValue'] = row['code_value']
					item['codeStep'] = row['code_step']
					item['codeSort'] = row['code_sort']
					item['used'] = row['used']
					item['codeSub'] = get_common_code_list(row['parent_id'], '0', svt)
					itemList.append(item)

				data['codeList'] = itemList

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


	##############################################################
    # POST
    ##############################################################
	# swagger 파라미터
	swagger = SyCommon.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('codeId', type=str, required=False, location='body')
	swagger.add_argument('codeName', type=str, required=True, location='body')
	swagger.add_argument('codeValue', type=str, required=False, location='body')
	swagger.add_argument('codeStep', type=int, required=True, location='body')
	swagger.add_argument('used', type=str, required=True, location='body')
	@SyCommon.expect(swagger)

	@SyCommon.doc(model=SyCommonPost)

	def post(self):
		"""
		메뉴정보 등록
		필수 : Authorization, codeName, codeStep, used,
		일반 : codeId, codeValue, codeValue2, codeValue3
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
		parser.add_argument('codeId', type=str, required=False)
		parser.add_argument('codeName', type=str, required=True)
		parser.add_argument('codeValue', type=str, required=False)
		parser.add_argument('codeStep', type=int, required=True)
		parser.add_argument('used', type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'codeName' not in parameter or not parameter['codeName']:
				hasParam = False

			if 'codeStep' not in parameter or not parameter['codeStep']:
				hasParam = False

			if 'used' not in parameter or not parameter['used']:
				hasParam = False


			if hasParam :
				# parameter 정리
				codeName = parameter['codeName']
				codeStep = parameter['codeStep']
				used = parameter['used']

				codeId = ''
				if 'codeId' in parameter and parameter['codeId'] != '':
					codeId = parameter['codeId']

				codeValue = ''
				if 'codeValue' in parameter and parameter['codeValue'] != '':
					codeValue = parameter['codeValue']

				if codeId == '':
					# 1차
					sql = """SELECT LPAD(IFNULL(MAX(CONVERT(SUBSTR(code_id, 1, 2),UNSIGNED)),0)+1, 2, 0) AS max_code_id
					FROM sy_common
					WHERE code_step = %s"""
					cursor.execute(query=sql, args=codeStep)
					result = cursor.fetchone()
					newCodeId = str(result['max_code_id']) + '0000'
					parentId = newCodeId

				else:
					# 2차
					sql = """SELECT LPAD(IFNULL(MAX(CONVERT(SUBSTR(code_id, 3, 2),UNSIGNED)),0)+1, 2, 0) AS max_code_id
					FROM sy_common
					WHERE parent_id = %s and code_step = %s"""
					cursor.execute(query=sql, args=(codeId, codeStep))
					result = cursor.fetchone()

					newCodeId = codeId[:2] + str(result['max_code_id']) + '00'
					parentId = codeId

				sql = "SELECT max(code_sort)+1 max_code_sort FROM sy_common"
				cursor.execute(query=sql)
				sort = cursor.fetchone()
				if sort['max_code_sort'] is None:
					codeSort = 1
				else:
					codeSort = sort['max_code_sort']

				# 저장
				sql = """INSERT INTO sy_common(code_id, parent_id, code_step, code_sort, code_name, code_value, used, insert_id, insert_dt, insert_ip)
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
				cursor.execute(query=sql, args=(newCodeId, parentId, codeStep, codeSort, codeName, codeValue, used, payload['userId'], datetime.datetime.now(), userIp))

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



	##############################################################
    # PUT
    ##############################################################
	# swagger 파라미터
	swagger = SyCommon.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('codeId', type=str, required=True, location='body')
	swagger.add_argument('codeName', type=str, required=True, location='body')
	swagger.add_argument('codeValue', type=str, required=False, location='body')
	swagger.add_argument('used', type=str, required=True, location='body')
	@SyCommon.expect(swagger)

	@SyCommon.doc(model=SyCommonPut)

	def put(self):
		"""
		메뉴정보 수정
		필수 : Authorization, codeId, codeName, used
		일반 : codeValue, codeValue2, codeValue3
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
		parser.add_argument('codeName', type=str, required=True)
		parser.add_argument('codeValue', type=str, required=False)
		parser.add_argument('used', type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True
			# if 'pageId' not in parameter or not parameter['pageId']:
			# 	hasParam = False
			if 'codeId' not in parameter or not parameter['codeId']:
				hasParam = False

			if 'codeName' not in parameter or not parameter['codeName']:
				hasParam = False

			if 'used' not in parameter or not parameter['used']:
				hasParam = False

			if hasParam :
				# parameter 정리
				codeId = parameter['codeId']
				codeName = parameter['codeName']
				used = parameter['used']

				codeValue = ''
				if 'codeValue' in parameter and parameter['codeValue'] != '':
					codeValue = parameter['codeValue']


				sql = """UPDATE sy_common SET code_name = %s, code_value = %s, used = %s
				WHERE code_id = %s"""
				cursor.execute(query=sql, args=(codeName, codeValue, used, codeId))

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


	##############################################################
    # DELETE
    ##############################################################
	# swagger 파라미터
	swagger = SyCommon.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('codeId', type=str, required=True, location='body')
	@SyCommon.expect(swagger)

	@SyCommon.doc(model=SyCommonDelete)

	def delete(self):
		"""
		공통코드 삭제
		필수 : Authorization, codeId
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
		parser.add_argument('codeId', type=str, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True
			# if 'pageId' not in parameter or not parameter['pageId']:
			# 	hasParam = False
			if 'codeId' not in parameter or not parameter['codeId']:
				hasParam = False

			if hasParam :
				# parameter 정리
				codeId = parameter['codeId']

				sql = """SELECT code_step, (CASE WHEN code_step = 1
				THEN (SELECT COUNT(*) FROM sy_common WHERE code_step <> 1 AND parent_id = %s)  ELSE 0 END) AS codeSubCount
				FROM sy_common
				WHERE code_id = %s"""
				cursor.execute(query=sql, args=(codeId, codeId))
				result = cursor.fetchone()

				if result['codeSubCount'] < 1:
					sql = "DELETE FROM sy_common WHERE code_id = %s"
					cursor.execute(query=sql, args=codeId)

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
