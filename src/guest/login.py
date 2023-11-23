# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

Login = Namespace('login')

#메소드별 모델 생성
LoginPost = Login.schema_model('LoginPost',

)

@Login.route('',methods=['POST'])
class LoginApi(Resource):

	# swagger 파라미터
	swagger=Login.parser()
	swagger.add_argument('userId', required=True, location='body')
	swagger.add_argument('password', required=True, location='body')
	@Login.expect(swagger)

	# Example Value
	@Login.doc(model=LoginPost)

	def post(self):
		"""
		로그인
		필수 : userId, password
		일반 :
		"""

		statusCode=200
		data={'timestamp': datetime.datetime.now().isoformat()}

		# host 정보
		svt, host, userIp=get_server_type(request)

		# 파라미터 정리
		parser=reqparse.RequestParser()
		parser.add_argument('userId', type=str, required=True)
		parser.add_argument('password', type=str, required=True)
		parameter=parser.parse_args()

		# DB 시작
		cursor=mysql_cursor(mysql_conn(svt))

		try:
			hasParam=True

			# 필수값 체크
			if 'userId' not in parameter or not parameter['userId']:
				hasParam=False

			if 'password' not in parameter or not parameter['password']:
				hasParam=False

			# 필수 값 체크
			if hasParam:
				userId=parameter['userId']
				password=parameter['password']

				# sql 구문보기
				sql="""
				SELECT
					seq,
					user_id,
					user_name,
					role,
					login_yn,
					delete_id
				FROM
					sy_user
				WHERE
					user_id = %s
					AND password = SHA2(%s, 256)
					AND delete_id IS NULL
				"""
				cursor.execute(query=sql, args=(userId, password))
				result=cursor.fetchone()

				if result is not None:

					if result['login_yn'] == 'Y':

						seq = result['seq']
						userId = result['user_id']
						userName = result['user_name']
						role=int(result['role'])

						# token 생성
						token=jwt_token_generator(seq=seq, userName=userName, userId=userId, role=role)
						refresh_token = jwt_refresh_token_generator(seq)

						# 토큰 업데이트
						sql="""UPDATE sy_user
						SET last_login_dt= %s, last_login_ip = %s, login_count = login_count+1
						WHERE seq = %s"""
						cursor.execute(query=sql, args=(datetime.datetime.now(), userIp, seq))

						data['userNo'] = seq
						data['userId']= userId
						data['userName']= userName
						data['role']= role
						data['token'] = token
						data['refresh_token'] = refresh_token

					else:
						statusCode=404
						data['error']='사용 제한이 된 사용자 입니다. '

				else:
					statusCode=404
					data['error']='아이디나 비밀번호가 일치하지 않습니다.'
			else:
				statusCode=404
				data['error']='No Parameter'

		except Exception as e:
			logging.error(traceback.format_exc())
			data['error']='exception error'
			statusCode=505
			return data, statusCode

		finally:
			# DB종료
			cursor.close()

		return json_null_to_empty(data), statusCode
