# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

PjKeyword = Namespace('PjKeyword')

PjKeywordGet = PjKeyword.schema_model('PjKeywordGet', {
})
PjKeywordPost = PjKeyword.schema_model('PjKeywordPost', {
})
PjKeywordPut = PjKeyword.schema_model('PjKeywordPut', {
})
PjKeywordDelete = PjKeyword.schema_model('PjKeywordDelete', {
})
@PjKeyword.route('', methods=['GET','POST','PUT','DELETE'])
class PjKeywordApi(Resource):
	####################################################################################################################
	# METHOD : GET
	# write  : 23.03.31
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = PjKeyword.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	# swagger.add_argument('title', type=int, required=True, location='body', help='회원번호')
	@PjKeyword.expect(swagger)

	@PjKeyword.doc(model=PjKeywordGet)

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
			data['error'] = '접근 권한이 없습니다.'
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
						pj_keyword
					WHERE
						delete_id IS NULL """

				if payload['role'] < 5:
					sql += "AND user_seq = %s " % payload['userNo']

				sql += "ORDER BY title ASC"

				cursor.execute(query=sql)

				itemList = []
				for idx, row in enumerate(cursor.fetchall()):
					item = {}
					item['keywordNo'] = row['seq']
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
	swagger = PjKeyword.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('title',         type=str, required=True, location='body')
	@PjKeyword.expect(swagger)

	@PjKeyword.doc(model=PjKeywordPost)

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

				sql = "SELECT * FROM pj_keyword WHERE delete_id IS NULL AND REPLACE(title, ' ', '') = %s"
				cursor.execute(query=sql, args=titleRes)
				res = cursor.fetchone()

				if res is None:

					# transation 시작
					conn.begin()
					try:
						# 카테고리 등록
						sql = """
							INSERT INTO pj_keyword(user_seq, title, insert_id, insert_ip)
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
					data['error'] = '키워드 중복'

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
	swagger = PjKeyword.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('keywordNo', type=str, required=True, location='body')
	swagger.add_argument('title',     type=str, required=True, location='body')
	@PjKeyword.expect(swagger)

	@PjKeyword.doc(model=PjKeywordPut)

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
		parser.add_argument('keywordNo', type=str, required=True)
		parser.add_argument('title',      type=str, required=True)
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True
			if 'keywordNo' not in parameter or not parameter['keywordNo']:
				hasParam = False

			if 'title' not in parameter or not parameter['title']:
				hasParam = False

			if hasParam :

				keywordNo = parameter['keywordNo']
				title = parameter['title']

				# 공백 제거
				titleRes = title.replace(" ", "")

				# 중복체크
				sql = """
					SELECT
						*
					FROM
						pj_keyword
					WHERE
						delete_id IS NULL
						AND REPLACE(title, ' ', '') = '%s'
						AND user_seq = %s
						AND seq <> %s """ % (titleRes, payload['userNo'], keywordNo)
				cursor.execute(query=sql)
				res = cursor.fetchone()

				if res is None:

					# transation 시작
					conn.begin()
					try:
						# 키워드 수정
						sql = """
							UPDATE pj_keyword SET
								title = %s,
								update_id = %s,
								update_ip = %s
							WHERE
								seq = %s
						"""
						cursor.execute(query=sql, args=(title, payload['userId'], userIp, keywordNo))


					except Exception as e:
						conn.rollback()
						raise

					else:
						conn.commit()

				else:
					statusCode = 404
					data['error'] = '키워드 중복'

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
	swagger = PjKeyword.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('keywordNo', type=int, required=False, location='body', help='pj_category.seq')
	@PjKeyword.expect(swagger)

	@PjKeyword.doc(model=PjKeywordDelete)

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
		parser.add_argument('keywordNo', type=int, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'keywordNo' not in parameter or not parameter['keywordNo']:
				hasParam = False

			if hasParam :
				keywordNo = parameter['keywordNo']

				sql = "DELETE FROM pj_keyword WHERE seq = %s"
				cursor.execute(query=sql, args=keywordNo)

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
