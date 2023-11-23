# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *


GnCheckDuplicate = Namespace('GnCheckDuplicate')

GnCheckDuplicateGet = GnCheckDuplicate.schema_model('GnCheckDuplicateGet', {
})

@GnCheckDuplicate.route('', methods=['GET'])
class GnCheckDuplicateApi(Resource):
	##############################################################
	# GET
	##############################################################
	# swagger 파라미터
	swagger = GnCheckDuplicate.parser()
	swagger.add_argument('Authorization', required=True,  location='headers', help='로그인토큰')
	swagger.add_argument('key', type=str, required=True,  location='body', help='검색 타입')
	swagger.add_argument('val', type=str, required=True,  location='body', help='검색 내용')
	@GnCheckDuplicate.expect(swagger)

	@GnCheckDuplicate.doc(model=GnCheckDuplicateGet)

	def get(self):
		"""
		회원리스트
		필수 : Authorization, key, val
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
		if payload['role'] < 3:
			data['error'] = '사용 권한이 없습니다'
			return data, 401

		# 파라미터 정리
		parser=reqparse.RequestParser()
		parser.add_argument('key', type=str, required=True,  location='args')
		parser.add_argument('val', type=str, required=True,  location='args')

		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'key' not in parameter or not parameter['key']:
				hasParam = False

			if 'val' not in parameter or not parameter['val']:
				hasParam = False

			if hasParam :
				key = parameter['key']
				val = parameter['val']

				if key is not None and val is not None:
					if key == 'userId':
						# 회원 ID 중복 체크
						sql = """SELECT COUNT(*) AS cnt FROM sy_user WHERE user_id = %s """
						cursor.execute(query=sql, args=val)
						result = cursor.fetchone()

					elif key == 'storeId':
						# 판매점 ID 중복 체크
						sql = """
							SELECT COUNT(*) AS cnt FROM pj_store
							WHERE delete_id IS NULL AND store_id = %s AND user_seq = %s
						"""
						cursor.execute(query=sql, args=(val, payload['userNo']))
						result = cursor.fetchone()

					if result['cnt'] < 1:
						checkResult = True
					else:
						checkResult = False

					data['checkResult'] = checkResult

				else:
					statusCode = 404
					data['error'] = '비정상적인 접근 입니다'


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
