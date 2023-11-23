# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

MdKeywordList = Namespace('MdKeywordList')

MdKeywordListGet = MdKeywordList.schema_model('MdKeywordListGet', {
})

@MdKeywordList.route('', methods=['GET'])
class MdKeywordListApi(Resource):
	####################################################################################################################
	# METHOD : GET
	# write  : 23.07.06
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = MdKeywordList.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	@MdKeywordList.expect(swagger)

	@MdKeywordList.doc(model=MdKeywordListGet)

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
						title
					FROM
						pj_keyword
					WHERE
						used = 1
						AND user_seq = %s
					ORDER BY
						seq ASC
				"""
				cursor.execute(query=sql, args=payload['userNo'])

				itemList = []
				for idx, row in enumerate(cursor.fetchall()):
					item = {}
					item['keywordNo'] = row['seq']
					item['title'] = row['title']
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


