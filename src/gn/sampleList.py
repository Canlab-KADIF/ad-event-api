# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

PjStoreList = Namespace('PjStoreList')

PjStoreListGet = PjStoreList.schema_model('PjStoreListGet', {

})

@PjStoreList.route('', methods=['GET'])
class PjStoreListApi(Resource):
	####################################################################################################################
	# METHOD : GET
	# write  : 23.06.30
	# writer : chside
	####################################################################################################################
	swagger = PjStoreList.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('searchRole', required=False, type=str, location='body', help='권한')
	swagger.add_argument('searchText', required=False, type=str, location='body', help='검색어')
	swagger.add_argument('page', required=False, type=int, location='body', help='페이지 번호 default : 1 ')
	swagger.add_argument('pageSize', required=False, type=int, location='body', help='페이지당 데이터수 default : 20')
	@PjStoreList.expect(swagger)

	@PjStoreList.doc(model=PjStoreListGet)

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
			data['error'] = '회원만 접속 가능합니다.'
			return data, 401

		# 파라미터 정리
		parser=reqparse.RequestParser()
		parser.add_argument('searchRole', type=str, required=False, location='args')
		parser.add_argument('searchText', type=str, required=False, location='args')
		parser.add_argument('page', type=int, required=False, location='args')
		parser.add_argument('pageSize', type=int, required=False, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if hasParam :

				searchRole = None
				if parameter['searchRole'] is not None:
					searchRole = parameter['searchRole']

				searchText = None
				if  parameter['searchText'] is not None:
					searchText = parameter['searchText']

				page = 1
				if parameter['page'] is not None:
					page = parameter['page']

				pageSize = 10
				if parameter['pageSize'] is not None:
					pageSize = parameter['pageSize']

				# field
				total_field = "COUNT(*) as cnt "
				sql_field = """
				s.seq,
				s.user_seq,
				u.user_name,
				s.store_id,
				s.store_name,
				s.buyer_name,
				s.used,
				s.insert_dt """

				# table
				sql_table = """
				pj_store s
				LEFT JOIN sy_user u ON u.seq = s.user_seq
				"""

				# where
				sql_where = "(1=1) "

				# if searchRole is not None:
				# 	if searchRole == '0':
				# 		sql_where = sql_where + ""
				# 	else:
				# 		sql_where = sql_where + "AND u.role = '%s' " % searchRole

				if searchText is not None:
					sql_where = sql_where + "AND (store_name LIKE '%%%s%%' " % (searchText, searchText)

				# order by
				sql_order = "s.seq DESC "

				# limit
				sql_limit = "%s, %s " % (pageSize * (page-1), pageSize)

				# 전체 게시글 수
				sql = """SELECT %s FROM %s WHERE %s""" % (total_field, sql_table, sql_where)
				cursor.execute(query=sql)
				total_result = cursor.fetchone()
				data['totalCount'] = total_result['cnt']

				# list
				sql = """
				SELECT %s
				FROM %s
				WHERE %s
				ORDER BY %s
				LIMIT %s""" % (sql_field, sql_table, sql_where, sql_order, sql_limit)
				cursor.execute(query=sql)

				itemList = []
				for idx, row in enumerate(cursor.fetchall()):
					item={}
					item['no'] = (total_result['cnt'] - pageSize*(page - 1) - idx)
					item['storeNo'] = row['seq']
					item['userNo'] = row['user_seq']
					item['userName'] = row['user_name']
					item['storeId'] = row['store_id']
					item['storeName'] = row['store_name']
					item['buyerName'] = row['buyer_name']

					item['used'] = row['used']
					if row['used'] == '1':
						item['usedNm'] = '사 용'
					else:
						item['usedNm'] = '중 지'

					if row['insert_dt'] is not None:
						item['insertDt'] = row['insert_dt'].strftime("%Y-%m-%d")
						# item['lastLoginDt'] = row['last_login_dt'].strftime("%Y-%m-%d %H:%M:%S")
					else:
						item['insertDt'] = ''

					itemList.append(item)

				data['page'] = page
				data['pageSize'] = pageSize
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

