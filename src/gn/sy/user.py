# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

SyUser = Namespace('SyUser')

SyUserGet = SyUser.schema_model('SyUserGet', {
})
SyUserPost = SyUser.schema_model('SyUserPost', {
})
SyUserPut = SyUser.schema_model('SyUserPut', {
})
SyUserDelete = SyUser.schema_model('SyUserDelete', {
})
@SyUser.route('', methods=['GET','POST','PUT','DELETE'])
class SyUserApi(Resource):
	####################################################################################################################
	# METHOD : GET
	# write  : 23.03.31
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = SyUser.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('userNo', type=int, required=True, location='body', help='회원번호')
	@SyUser.expect(swagger)

	@SyUser.doc(model=SyUserGet)

	def get(self):
		"""
		회원리스트
		필수 :
		일반 : searchType, searchText, page, pageSize
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
		parser.add_argument('userNo', type=int, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'userNo' not in parameter or not parameter['userNo']:
				hasParam = False

			if hasParam :
				userNo = parameter['userNo']
				sql = """
					SELECT
						user_id,
						user_name,
						`role`,
						login_yn,
						mobile,
						tel,
						email,
						gender,
						birth_dt,
						post_code,
						address,
						address_detail,
						group_type,
						group_name,
						group_position,
						enter_dt,
						last_login_dt,
						memo
					FROM
						sy_user
					WHERE
						seq = %s
				"""
				cursor.execute(query=sql, args=userNo)
				row = cursor.fetchone()

				data['userId'] = row['user_id']
				data['userName'] = row['user_name']
				data['role'] = row['role']
				data['loginYn'] = row['login_yn']
				data['mobile'] = row['mobile']
				data['tel'] = row['tel']
				data['email'] = row['email']
				data['gender'] = row['gender']
				data['birthDt'] = ''
				if row['birth_dt'] is not None:
					data['birthDt'] = row['birth_dt'].strftime("%Y-%m-%d")

				data['postCode'] = row['post_code']
				data['address'] = row['address']
				data['addressDetail'] = row['address_detail']
				data['groupType'] = row['group_type']
				data['groupName'] = row['group_name']
				data['groupPosition'] = row['group_position']
				data['enterDt'] = ''
				if row['enter_dt'] is not None:
					data['enterDt'] = row['enter_dt'].strftime("%Y-%m-%d")

				data['memo'] = row['memo']

				# if row['insert_dt'] is not None:
				#     data['insertDt'] = row['insert_dt'].strftime("%Y-%m-%d %H:%M:%S")
				# else:
				#     row['insert_dt'] = ''

				# data['insertIp'] = row['insert_ip']

				# if row['password_change_dt'] is not None:
				#     data['pwdChangeDt'] = row['password_change_dt'].strftime("%Y-%m-%d %H:%M:%S")
				# else:
				#     data['pwdChangeDt'] = ''

				# if row['update_dt'] is not None:
				#     data['updateDt'] = row['update_dt'].strftime("%Y-%m-%d %H:%M:%S")
				# else:
				#     data['updateDt'] = ''
				# data['updateIp'] = row['update_ip']

				# if row['last_login_dt'] is not None:
				#     data['lastLoginDt'] = row['last_login_dt'].strftime("%Y-%m-%d %H:%M:%S")
				# else:
				#     data['lastLoginDt'] = ''

				# data['lastLoginIp'] = row['last_login_ip']
				# data['loginCount'] = row['login_count']


				data['roleList'] = get_common_code_list('010000', '1', svt)
				data['groupTypeList'] = get_common_code_list('020000', '1', svt)

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
	# write  : 23.03.31
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = SyUser.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('userId',        type=str, required=True, location='body')
	swagger.add_argument('password',      type=str, required=True, location='body')
	swagger.add_argument('userName',      type=str, required=True, location='body')
	swagger.add_argument('birthDt',       type=str, required=False, location='body')
	swagger.add_argument('mobile',        type=str, required=True, location='body')
	swagger.add_argument('gender',        type=str, required=False, location='body')
	swagger.add_argument('tel',           type=str, required=False, location='body')
	swagger.add_argument('email',         type=str, required=False, location='body')
	swagger.add_argument('groupName',     type=str, required=False, location='body')
	swagger.add_argument('groupType',     type=str, required=False, location='body')
	swagger.add_argument('groupPosition', type=str, required=False, location='body')
	swagger.add_argument('enterDt',       type=str, required=False, location='body')
	swagger.add_argument('postCode',      type=str, required=False, location='body')
	swagger.add_argument('address',       type=str, required=False, location='body')
	swagger.add_argument('addressDetail', type=str, required=False, location='body')
	swagger.add_argument('role',          type=int, required=True,  location='body')
	swagger.add_argument('loginYn',       type=str, required=True, location='body')
	swagger.add_argument('memo',          type=str, required=False, location='body')
	@SyUser.expect(swagger)

	@SyUser.doc(model=SyUserPost)

	def post(self):
		"""
		회원정보 등록
		필수 : Authorization, userId, password, userName, userLevel, loginYn
		일반 : email, addressDetail, memo
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

		parser.add_argument('userId',        type=str, required=True)
		parser.add_argument('password',      type=str, required=True)
		parser.add_argument('userName',      type=str, required=True)
		parser.add_argument('birthDt',       type=str, required=False)
		parser.add_argument('mobile',        type=str, required=True)
		parser.add_argument('gender',        type=str, required=False)
		parser.add_argument('tel',           type=str, required=False)
		parser.add_argument('email',         type=str, required=False)
		parser.add_argument('groupName',     type=str, required=False)
		parser.add_argument('groupType',     type=str, required=False)
		parser.add_argument('groupPosition', type=str, required=False)
		parser.add_argument('enterDt',       type=str, required=False)
		parser.add_argument('postCode',      type=str, required=False)
		parser.add_argument('address',       type=str, required=False)
		parser.add_argument('addressDetail', type=str, required=False)
		parser.add_argument('role',          type=str, required=False)
		parser.add_argument('loginYn',       type=str, required=False)
		parser.add_argument('memo',          type=str, required=False)
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True

			if 'userId' not in parameter or not parameter['userId']:
				hasParam = False

			if 'password' not in parameter or not parameter['password']:
				hasParam = False

			if 'userName' not in parameter or not parameter['userName']:
				hasParam = False

			if 'mobile' not in parameter or not parameter['mobile']:
				hasParam = False

			if 'role' not in parameter or not parameter['role']:
				hasParam = False

			if 'loginYn' not in parameter or not parameter['loginYn']:
				hasParam = False

			if hasParam :

				userId = parameter['userId']
				password = parameter['password']
				userName = parameter['userName']
				mobile = parameter['mobile']
				role = parameter['role']
				loginYn = parameter['loginYn']

				birthDt = None
				if 'birthDt' in parameter and parameter['birthDt'] != '':
					birthDt = parameter['birthDt']

				gender = None
				if 'gender' in parameter and parameter['gender'] != '':
					gender = parameter['gender']

				tel = None
				if 'tel' in parameter and parameter['tel'] != '':
					tel = parameter['tel']

				email = None
				if 'email' in parameter and parameter['email'] != '':
					email = parameter['email']

				groupName = None
				if 'groupName' in parameter and parameter['groupName'] != '':
					groupName = parameter['groupName']

				groupType = None
				if 'groupType' in parameter and parameter['groupType'] != '':
					groupType = parameter['groupType']

				groupPosition = None
				if 'groupPosition' in parameter and parameter['groupPosition'] != '':
					groupPosition = parameter['groupPosition']

				enterDt = None
				if 'enterDt' in parameter and parameter['enterDt'] != '':
					enterDt = parameter['enterDt']

				postCode = None
				if 'postCode' in parameter and parameter['postCode'] != '':
					postCode = parameter['postCode']

				address = None
				if 'address' in parameter and parameter['address'] != '':
					address = parameter['address']

				addressDetail = None
				if 'addressDetail' in parameter and parameter['addressDetail'] != '':
					addressDetail = parameter['addressDetail']

				memo = None
				if 'memo' in parameter and parameter['memo'] != '':
					memo = parameter['memo']



				sql = "SELECT COUNT(*) AS cnt FROM sy_user WHERE user_id = %s"
				cursor.execute(query=sql, args=userId)
				res = cursor.fetchone()

				if res['cnt'] < 1 :

					# transation 시작
					conn.begin()
					try:

						# 회원 등록
						sql = """
							INSERT INTO sy_user(user_id, password, user_name, role, login_yn, mobile, tel, email, gender, birth_dt, post_code, address, address_detail, group_type, group_name, group_position, enter_dt, memo, insert_id, insert_ip)
							VALUES(%s, SHA2(%s, 256), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
						"""
						cursor.execute(query=sql, args=(userId, password, userName, role, loginYn, mobile, tel, email, gender, birthDt, postCode, address, addressDetail, groupType, groupName, groupPosition, enterDt, memo, payload['userId'], userIp))
						data['userNo'] = cursor.lastrowid


						# 회원 추가정보


					except Exception as e:
						conn.rollback()
						raise

					else:
						conn.commit()

				else:
					statusCode = 404
					data['error'] = 'ID 중복'

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
	# write  : 23.03.31
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = SyUser.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('userNo',        type=str, required=True, location='body')
	swagger.add_argument('userName',      type=str, required=True, location='body')
	# swagger.add_argument('password',      type=str, required=False, location='body')
	swagger.add_argument('birthDt',       type=str, required=False, location='body')
	swagger.add_argument('mobile',        type=str, required=True, location='body')
	swagger.add_argument('gender',        type=str, required=False, location='body')
	swagger.add_argument('tel',           type=str, required=False, location='body')
	swagger.add_argument('email',         type=str, required=False, location='body')
	swagger.add_argument('groupName',     type=str, required=False, location='body')
	swagger.add_argument('groupType',     type=str, required=False, location='body')
	swagger.add_argument('groupPosition', type=str, required=False, location='body')
	swagger.add_argument('enterDt',       type=str, required=False, location='body')
	swagger.add_argument('postCode',      type=str, required=False, location='body')
	swagger.add_argument('address',       type=str, required=False, location='body')
	swagger.add_argument('addressDetail', type=str, required=False, location='body')
	swagger.add_argument('role',          type=int, required=True,  location='body')
	swagger.add_argument('loginYn',       type=str, required=True, location='body')
	swagger.add_argument('memo',          type=str, required=False, location='body')

	@SyUser.expect(swagger)

	@SyUser.doc(model=SyUserPut)

	def put(self):
		"""
		회원정보 수정
		필수 : Authorization, userNo, userName, role, loginYn
		일반 : password, birthDt, gender, tel, email, groupName, groupType, groupPosition, enterDt,
		  	   postCode, address, addressDetail, memo
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
		parser.add_argument('userNo',       type=int, required=True)
		parser.add_argument('userName',      type=str, required=True)
		# parser.add_argument('password',      type=str, required=False)
		parser.add_argument('birthDt',       type=str, required=False)
		parser.add_argument('mobile',        type=str, required=True)
		parser.add_argument('gender',        type=str, required=False)
		parser.add_argument('tel',           type=str, required=False)
		parser.add_argument('email',         type=str, required=False)
		parser.add_argument('groupName',     type=str, required=False)
		parser.add_argument('groupType',     type=str, required=False)
		parser.add_argument('groupPosition', type=str, required=False)
		parser.add_argument('enterDt',       type=str, required=False)
		parser.add_argument('postCode',      type=str, required=False)
		parser.add_argument('address',       type=str, required=False)
		parser.add_argument('addressDetail', type=str, required=False)
		parser.add_argument('role',          type=int, required=True)
		parser.add_argument('loginYn',       type=str, required=True)
		parser.add_argument('memo',          type=str, required=False)
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True
			if 'userNo' not in parameter or not parameter['userNo']:
				hasParam = False

			if 'userName' not in parameter or not parameter['userName']:
				hasParam = False

			if 'mobile' not in parameter or not parameter['mobile']:
				hasParam = False

			if 'role' not in parameter or not parameter['role']:
				hasParam = False

			if 'loginYn' not in parameter or not parameter['loginYn']:
				hasParam = False

			if hasParam :
				userNo = parameter['userNo']
				userName = parameter['userName']
				mobile = parameter['mobile']
				role = parameter['role']
				loginYn = parameter['loginYn']

				# password = None
				# if 'password' in parameter and parameter['password'] != '':
				# 	password = parameter['password']

				birthDt = None
				if 'birthDt' in parameter and parameter['birthDt'] != '':
					birthDt = parameter['birthDt']

				gender = None
				if 'gender' in parameter and parameter['gender'] != '':
					gender = parameter['gender']

				tel = None
				if 'tel' in parameter and parameter['tel'] != '':
					tel = parameter['tel']

				email = None
				if 'email' in parameter and parameter['email'] != '':
					email = parameter['email']

				groupName = None
				if 'groupName' in parameter and parameter['groupName'] != '':
					groupName = parameter['groupName']

				groupType = None
				if 'groupType' in parameter and parameter['groupType'] != '':
					groupType = parameter['groupType']

				groupPosition = None
				if 'groupPosition' in parameter and parameter['groupPosition'] != '':
					groupPosition = parameter['groupPosition']

				enterDt = None
				if 'enterDt' in parameter and parameter['enterDt'] != '':
					enterDt = parameter['enterDt']

				postCode = None
				if 'postCode' in parameter and parameter['postCode'] != '':
					postCode = parameter['postCode']

				address = None
				if 'address' in parameter and parameter['address'] != '':
					address = parameter['address']

				addressDetail = None
				if 'addressDetail' in parameter and parameter['addressDetail'] != '':
					addressDetail = parameter['addressDetail']

				memo = ''
				if 'memo' in parameter and parameter['memo'] != '':
					memo = parameter['memo']


				today = datetime.datetime.now()

				sql = "SELECT user_id FROM sy_user WHERE seq = %s "
				cursor.execute(query=sql, args=userNo)
				result = cursor.fetchone()

				if result is not None:
					# transation 시작
					conn.begin()
					try:

						sql = """
							UPDATE sy_user SET
								user_name = %s,
								role = %s,
								login_yn = %s,
								mobile = %s,
								tel = %s,
								email = %s,
								gender = %s,
								post_code = %s,
								address = %s,
								address_detail = %s,
								group_type = %s,
								group_name = %s,
								group_position = %s,
								memo = %s,
								birth_dt = %s,
								enter_dt = %s,
								update_id = %s,
								update_ip = %s
							WHERE
								seq = %s
						"""
						cursor.execute(query=sql, args=(userName, role, loginYn, mobile, tel, email, gender, postCode, address, addressDetail, groupType, groupName, groupPosition, memo, birthDt, enterDt, payload['userId'], userIp, userNo))

					except Exception as e:
						conn.rollback()
						raise

					else:
						conn.commit()

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


	####################################################################################################################
	# METHOD : DELETE
	# write  : 23.03.31
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = SyUser.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('userNo', type=int, required=False, location='body', help='user.seq')
	@SyUser.expect(swagger)

	@SyUser.doc(model=SyUserDelete)

	def delete(self):
		"""
		회원정보 삭제
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
		# parser.add_argument('pageId', type=str, required=True, location='args')
		parser.add_argument('userNo', type=int, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'userNo' not in parameter or not parameter['userNo']:
				hasParam = False

			if hasParam :
				userNo = parameter['userNo']

				sql = "SELECT * FROM sy_user WHERE seq = %s"
				cursor.execute(query=sql, args=userNo)
				result = cursor.fetchone()

				if result is not None:

					today = datetime.datetime.now()

					sql = """
					UPDATE sy_user SET
					delete_id=%s, delete_dt=%s, delete_ip=%s
					WHERE seq=%s
					"""
					cursor.execute(query=sql, args=(payload['userId'], today, userIp, userNo))

				else:
					statusCode = 400
					data['error'] = '비정상적인 접근 입니다 '

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
