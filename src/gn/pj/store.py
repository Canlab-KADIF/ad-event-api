# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

PjStore = Namespace('PjStore')

PjStoreGet = PjStore.schema_model('PjStoreGet', {
})
PjStorePost = PjStore.schema_model('PjStorePost', {
})
PjStorePut = PjStore.schema_model('PjStorePut', {
})
PjStoreDelete = PjStore.schema_model('PjStoreDelete', {
})
@PjStore.route('', methods=['GET','POST','PUT','DELETE'])
class PjStoreApi(Resource):
	####################################################################################################################
	# METHOD : GET
	# write  : 23.03.31
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = PjStore.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('storeNo', type=str, required=True, location='body', help='판매점 번호')
	@PjStore.expect(swagger)

	@PjStore.doc(model=PjStoreGet)

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
		if payload['role'] < 3:
			data['error'] = '권한이 없습니다'
			return data, 401

		# 파라미터 정리
		parser=reqparse.RequestParser()
		parser.add_argument('storeNo', type=str, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'storeNo' not in parameter or not parameter['storeNo']:
				hasParam = False

			if hasParam :
				storeNo = parameter['storeNo']

				sql = """
					SELECT
						store_id,
						store_name,
						buyer_name,
						mobile,
						email,
						post_code,
						address,
						address_detail,
						enter_dt,
						memo,
						used,
						insert_dt
					FROM
						pj_store
					WHERE
						seq = %s """ % storeNo

				if payload['role'] < 5:
					sql += "AND user_seq = %s " % payload['userNo']

				cursor.execute(query=sql)
				row = cursor.fetchone()

				data['storeId'] = row['store_id']

				data['enterDt'] = ''
				if row['enter_dt'] is not None:
					data['enterDt'] = row['enter_dt'].strftime("%Y-%m-%d")

				data['storeName'] = row['store_name']
				data['buyerName'] = row['buyer_name']
				data['mobile'] = row['mobile']
				data['email'] = row['email']
				data['postCode'] = row['post_code']
				data['address'] = row['address']
				data['addressDetail'] = row['address_detail']


				data['memo'] = row['memo']
				data['used'] = row['used']

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
	swagger = PjStore.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('storeId',       type=str, required=True,  location='body')
	swagger.add_argument('storeName',     type=str, required=True,  location='body')
	swagger.add_argument('enterDt',       type=str, required=False, location='body')
	swagger.add_argument('buyerName',     type=str, required=False, location='body')
	swagger.add_argument('mobile',        type=str, required=False, location='body')
	swagger.add_argument('email',         type=str, required=False, location='body')
	swagger.add_argument('postCode',      type=str, required=False, location='body')
	swagger.add_argument('address',       type=str, required=False, location='body')
	swagger.add_argument('addressDetail', type=str, required=False, location='body')
	swagger.add_argument('memo',          type=str, required=False, location='body')
	@PjStore.expect(swagger)



	@PjStore.doc(model=PjStorePost)

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
		if payload['role'] < 3:
			data['error'] = '권한이 없습니다'
			return data, 401

		# 파라미터 정리
		parser=reqparse.RequestParser()
		parser.add_argument('storeId',       type=str, required=True)
		parser.add_argument('storeName',     type=str, required=True)
		parser.add_argument('enterDt',       type=str, required=False)
		parser.add_argument('buyerName',     type=str, required=False)
		parser.add_argument('mobile',   type=str, required=False)
		parser.add_argument('email',         type=str, required=False)
		parser.add_argument('postCode',      type=str, required=False)
		parser.add_argument('address',       type=str, required=False)
		parser.add_argument('addressDetail', type=str, required=False)
		parser.add_argument('memo',          type=str, required=False)
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True

			if 'storeId' not in parameter or not parameter['storeId']:
				hasParam = False

			if 'storeName' not in parameter or not parameter['storeName']:
				hasParam = False

			if hasParam :

				storeId = parameter['storeId']
				storeName = parameter['storeName']

				enterDt = None
				if 'enterDt' in parameter and parameter['enterDt'] != '':
					enterDt = parameter['enterDt']

				buyerName = None
				if 'buyerName' in parameter and parameter['buyerName'] != '':
					buyerName = parameter['buyerName']

				mobile = None
				if 'mobile' in parameter and parameter['mobile'] != '':
					mobile = parameter['mobile']

				email = None
				if 'email' in parameter and parameter['email'] != '':
					email = parameter['email']

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


				sql = """
					SELECT COUNT(*) AS cnt FROM pj_store
					WHERE delete_id IS NULL AND user_seq = %s AND store_id = %s
				"""
				cursor.execute(query=sql, args=(payload['userNo'], storeId))
				res = cursor.fetchone()

				if res['cnt'] < 1 :

					# transation 시작
					conn.begin()
					try:

						# 판매점 등록
						sql = """
							INSERT INTO pj_store(user_seq, store_id, store_name, buyer_name, mobile, email, post_code, address, address_detail, enter_dt, memo, insert_id, insert_ip)
							VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
						"""
						cursor.execute(query=sql, args=(payload['userNo'], storeId, storeName, buyerName, mobile, email, postCode, address, addressDetail, enterDt, memo, payload['userId'], userIp))
						data['storeNo'] = cursor.lastrowid


						# 추가정보


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
	swagger = PjStore.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('storeNo',       type=str, required=True, location='body')
	swagger.add_argument('storeName',     type=str, required=True, location='body')
	swagger.add_argument('enterDt',       type=str, required=False, location='body')
	swagger.add_argument('buyerName',     type=str, required=False, location='body')
	swagger.add_argument('mobile',        type=str, required=False, location='body')
	swagger.add_argument('email',         type=str, required=False, location='body')
	swagger.add_argument('postCode',      type=str, required=False, location='body')
	swagger.add_argument('address',       type=str, required=False, location='body')
	swagger.add_argument('addressDetail', type=str, required=False, location='body')
	swagger.add_argument('memo',          type=str, required=False, location='body')
	swagger.add_argument('used',          type=str, required=True,  location='used')

	@PjStore.expect(swagger)

	@PjStore.doc(model=PjStorePut)

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
		if payload['role'] < 3:
			data['error'] = '관리자만 접속 가능합니다.'
			return data, 401

		# 파라미터 정리
		parser=reqparse.RequestParser()
		parser.add_argument('storeNo',       type=str, required=True)
		parser.add_argument('storeName',     type=str, required=True)
		parser.add_argument('enterDt',       type=str, required=False)
		parser.add_argument('buyerName',     type=str, required=False)
		parser.add_argument('mobile',        type=str, required=False)
		parser.add_argument('email',         type=str, required=False)
		parser.add_argument('postCode',      type=str, required=False)
		parser.add_argument('address',       type=str, required=False)
		parser.add_argument('addressDetail', type=str, required=False)
		parser.add_argument('memo',          type=str, required=False)
		parser.add_argument('used',          type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True
			if 'storeNo' not in parameter or not parameter['storeNo']:
				hasParam = False

			if 'storeName' not in parameter or not parameter['storeName']:
				hasParam = False

			if 'used' not in parameter or not parameter['used']:
				hasParam = False

			if hasParam :
				storeNo = parameter['storeNo']
				storeName = parameter['storeName']
				used = parameter['used']

				enterDt = None
				if 'enterDt' in parameter and parameter['enterDt'] != '':
					enterDt = parameter['enterDt']

				buyerName = None
				if 'buyerName' in parameter and parameter['buyerName'] != '':
					buyerName = parameter['buyerName']

				gender = None
				if 'mobile' in parameter and parameter['mobile'] != '':
					mobile = parameter['mobile']

				email = None
				if 'email' in parameter and parameter['email'] != '':
					email = parameter['email']

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

				sql = "SELECT * FROM pj_store WHERE seq = %s "
				cursor.execute(query=sql, args=storeNo)
				result = cursor.fetchone()

				if result is not None:
					# transation 시작
					conn.begin()
					try:

						sql = """
							UPDATE pj_store SET
								store_name = %s,
								enter_dt = %s,
								buyer_name = %s,
								mobile = %s,
								email = %s,
								post_code = %s,
								address = %s,
								address_detail = %s,
								memo = %s,
								used = %s,
								update_id = %s,
								update_ip = %s
							WHERE
								seq = %s
						"""
						cursor.execute(query=sql, args=(storeName, enterDt, buyerName, mobile, email, postCode, address, addressDetail, memo, used, payload['userId'], userIp, storeNo))

						data['storeNo'] = storeNo

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
	swagger = PjStore.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('storeNo', type=int, required=True, location='body', help='pjStore.seq')
	@PjStore.expect(swagger)

	@PjStore.doc(model=PjStoreDelete)

	def delete(self):
		"""
		삭제
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
		parser.add_argument('storeNo', type=int, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'storeNo' not in parameter or not parameter['storeNo']:
				hasParam = False

			if hasParam :
				storeNo = parameter['storeNo']

				sql = "SELECT * FROM pj_store WHERE seq = %s"
				cursor.execute(query=sql, args=storeNo)
				result = cursor.fetchone()

				if result is not None:

					today = datetime.datetime.now()

					sql = """
					UPDATE pj_store SET
						delete_id=%s, delete_dt=%s, delete_ip=%s
					WHERE seq=%s
					"""
					cursor.execute(query=sql, args=(payload['userId'], today, userIp, storeNo))

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
