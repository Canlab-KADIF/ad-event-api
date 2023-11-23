# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *


SyUserResetPassword = Namespace('SyUserResetPassword')

SyUserResetPasswordPut = SyUserResetPassword.schema_model('SyUserResetPasswordPut', {
})

@SyUserResetPassword.route('', methods=['PUT'])
class SyUserResetPasswordApi(Resource):
	####################################################################################################################
	# METHOD : PUT
	# write  : 23.06.28
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = SyUserResetPassword.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('userNo', type=str, required=True, location='body', help='검색 타입')
	@SyUserResetPassword.expect(swagger)

	@SyUserResetPassword.doc(model=SyUserResetPasswordPut)

	def put(self):
		"""
		회원 비밀번호 리셋
		필수 : Authorization, userNo
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
		parser=reqparse.RequestParser()
		parser.add_argument('userNo', type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'userNo' not in parameter or not parameter['userNo']:
				hasParam = False

			if hasParam :
				userNo = parameter['userNo']

				today = datetime.datetime.now()

				sql = "SELECT * FROM sy_user WHERE seq = %s"
				cursor.execute(query=sql, args=userNo)
				result = cursor.fetchone()

				if result is not None:

					sql = """
						UPDATE sy_user SET
							password = SHA2(%s, 256),
							password_change_dt = %s,
							update_id = %s,
							update_ip = %s
						WHERE
							seq = %s
					"""
					cursor.execute(query=sql, args=(result['user_id'], today, payload['userId'], userIp, userNo))

				else:
					statusCode = 400
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
