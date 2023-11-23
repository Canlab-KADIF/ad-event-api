# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

PjCategory = Namespace('PjCategory')

PjCategoryGet = PjCategory.schema_model('PjCategoryGet', {
})
PjCategoryPost = PjCategory.schema_model('PjCategoryPost', {
})
PjCategoryPut = PjCategory.schema_model('PjCategoryPut', {
})
PjCategoryDelete = PjCategory.schema_model('PjCategoryDelete', {
})
@PjCategory.route('', methods=['GET','POST','PUT','DELETE'])
class PjCategoryApi(Resource):
	####################################################################################################################
	# METHOD : GET
	# write  : 23.03.31
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = PjCategory.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	# swagger.add_argument('title', type=int, required=True, location='body', help='회원번호')
	@PjCategory.expect(swagger)

	@PjCategory.doc(model=PjCategoryGet)

	def get(self):
		"""
		카테고리 리스트
		필수 :
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
			data['error'] = '관리자만 접속 가능합니다.'
			return data, 401

		# 파라미터 정리
		# parser=reqparse.RequestParser()
		# parser.add_argument('userNo', type=int, required=True, location='args')
		# parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			# if 'userNo' not in parameter or not parameter['userNo']:
			# 	hasParam = False

			if hasParam :
				# userNo = parameter['userNo']

				sql = """
					SELECT
						seq,
						title,
						user_seq,
						used
					FROM
						pj_category
					WHERE
						(1=1)
				"""
				if payload['role'] < 9:
					sql += "AND user_seq = %s" % payload['userNo']

				cursor.execute(query=sql)

				itemList = []
				for idx, row in enumerate(cursor.fetchall()):
					item = {}
					item['categoryNo'] = row['seq']
					item['title'] = row['title']
					item['userNo'] = row['user_seq']
					item['used'] = row['used']

					itemList.append(item)

				data['itemList'] = itemList

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
	swagger = PjCategory.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('title',         type=str, required=True, location='body')
	@PjCategory.expect(swagger)

	@PjCategory.doc(model=PjCategoryPost)

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
			data['error'] = '관리자만 접속 가능합니다.'
			return data, 401

		# 파라미터 정리
		parser=reqparse.RequestParser()

		parser.add_argument('title',        type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True

			if 'title' not in parameter or not parameter['title']:
				hasParam = False

			if hasParam :

				title = parameter['title']
				# 공백 제거
				titleRes = title.replace(" ", "")

				# 중복체크
				sql = """
					SELECT *
					FROM pj_category
					WHERE delete_id IS NULL AND REPLACE(title, ' ', '') = '%s' """ % titleRes

				if payload['role'] < 9:
					sql += "AND user_seq = %s " % payload['userNo']

				cursor.execute(query=sql)
				res = cursor.fetchone()

				if res is None:

					# transation 시작
					conn.begin()
					try:
						# 카테고리 등록
						sql = """
							INSERT INTO pj_category(user_seq, title, insert_id, insert_ip)
							VALUES(%s, %s, %s, %s)
						"""
						cursor.execute(query=sql, args=(payload['userNo'], title, payload['userId'], userIp))
						data['categoryNo'] = cursor.lastrowid

					except Exception as e:
						conn.rollback()
						raise

					else:
						conn.commit()

				else:
					statusCode = 404
					data['error'] = '카테고리 중복'

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
	swagger = PjCategory.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('categoryNo',    type=str, required=True, location='body')
	swagger.add_argument('title',         type=str, required=True, location='body')
	@PjCategory.expect(swagger)

	@PjCategory.doc(model=PjCategoryPost)

	def put(self):
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
			data['error'] = '관리자만 접속 가능합니다.'
			return data, 401

		# 파라미터 정리
		parser=reqparse.RequestParser()
		parser.add_argument('categoryNo', type=str, required=True)
		parser.add_argument('title',      type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True
			if 'categoryNo' not in parameter or not parameter['categoryNo']:
				hasParam = False

			if 'title' not in parameter or not parameter['title']:
				hasParam = False

			if hasParam :

				categoryNo = parameter['categoryNo']
				title = parameter['title']

				# 공백 제거
				titleRes = title.replace(" ", "")

				# 중복체크
				sql = """
					SELECT
						*
					FROM
						pj_category
					WHERE
						delete_id IS NULL
						AND REPLACE(title, ' ', '') = '%s'
						AND user_seq = %s
						AND seq <> %s """ % (titleRes, payload['userNo'], categoryNo)
				cursor.execute(query=sql)
				res = cursor.fetchone()

				if res is None:

					# transation 시작
					conn.begin()
					try:
						# 카테고리 수정
						sql = """
							UPDATE pj_category SET
								title = %s,
								update_id = %s,
								update_ip = %s
							WHERE
								seq = %s
						"""
						cursor.execute(query=sql, args=(title, payload['userId'], userIp, categoryNo))


					except Exception as e:
						conn.rollback()
						raise

					else:
						conn.commit()

				else:
					statusCode = 404
					data['error'] = '카테고리 중복'

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
	swagger = PjCategory.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('categoryNo', type=int, required=False, location='body', help='pj_category.seq')
	@PjCategory.expect(swagger)

	@PjCategory.doc(model=PjCategoryDelete)

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
		if payload['role'] < 3:
			data['error'] = '관리자만 접속 가능합니다.'
			return data, 401

		# 파라미터 정리
		parser=reqparse.RequestParser()
		# parser.add_argument('pageId', type=str, required=True, location='args')
		parser.add_argument('categoryNo', type=int, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'categoryNo' not in parameter or not parameter['categoryNo']:
				hasParam = False

			if hasParam :
				categoryNo = parameter['categoryNo']

				sql = "DELETE FROM pj_category WHERE seq = %s"
				cursor.execute(query=sql, args=categoryNo)

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
