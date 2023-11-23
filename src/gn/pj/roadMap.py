# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

PjRoadMap = Namespace('PjRoadMap')

PjRoadMapGet = PjRoadMap.schema_model('PjRoadMapGet', {

})

@PjRoadMap.route('', methods=['GET'])
class PjRoadMapApi(Resource):
	####################################################################################################################
	# METHOD : GET
	# write  : 23.08.23
	# writer : chside
	####################################################################################################################
	swagger = PjRoadMap.parser()
	swagger.add_argument('Authorization',  required=True, location='headers', help='로그인토큰')
	swagger.add_argument('searchSDT',      required=False, type=str, location='body', help='검색 시작일')
	swagger.add_argument('searchEDT',      required=False, type=str, location='body', help='검색 종료일')
	swagger.add_argument('searchProgress', required=False, type=int, location='body', help='진행 상태')
	swagger.add_argument('searchDamage',   required=False, type=str, location='body', help='파손 종류')
	swagger.add_argument('searchText', 	   required=False, type=str, location='body', help='검색어')
	swagger.add_argument('page', 		   required=False, type=int, location='body', help='페이지 번호')
	swagger.add_argument('pageSize',	   required=False, type=int, location='body', help='페이지당 데이터수')
	@PjRoadMap.expect(swagger)

	@PjRoadMap.doc(model=PjRoadMapGet)

	def get(self):
		"""
		회원리스트
		필수 :
		일반 : searchProgress, searchText, page, pageSize
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
		parser.add_argument('searchSDT',      required=False, type=str, location='args')
		parser.add_argument('searchEDT',      required=False, type=str, location='args')
		parser.add_argument('searchProgress', required=False, type=int, location='args')
		parser.add_argument('searchDamage',   required=False, type=str, location='args')
		parser.add_argument('searchText', 	  required=False, type=str, location='args')
		parser.add_argument('page', 		  required=False, type=int, location='args')
		parser.add_argument('pageSize', 	  required=False, type=int, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if hasParam :

				searchSDT = None
				if parameter['searchSDT'] is not None:
					searchSDT = parameter['searchSDT']

				searchEDT = None
				if parameter['searchEDT'] is not None:
					searchEDT = parameter['searchEDT']

				searchProgress = None
				if parameter['searchProgress'] is not None:
					searchProgress = parameter['searchProgress']

				searchDamage = None
				if parameter['searchDamage'] is not None:
					searchDamage = parameter['searchDamage']

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
				d.seq,
				d.lat,
				d.lng,
				d.damage_tp,
				(SELECT code_name FROM sy_common WHERE parent_id = '020000' AND code_step = 2 AND code_value = d.damage_tp) AS damageNm,
				d.progress_tp,
				(SELECT code_name FROM sy_common WHERE parent_id = '030000' AND code_step = 2 AND code_value = d.progress_tp) AS progressNm,
				u.user_name,
				d.end_dt,
				d.insert_id,
				d.insert_dt,
				d.memo """

				# table
				sql_table = """
				pj_damage d
				LEFT JOIN sy_user u ON u.user_id = d.insert_id
				"""

				# where
				sql_where = "d.delete_id IS NULL "

				if searchSDT and searchEDT:
					sql_where += "AND DATE_FORMAT(d.insert_dt, '%%Y-%%m-%%d') BETWEEN '%s' AND '%s' " % (searchSDT, searchEDT)

				if searchProgress is not None:
					if searchProgress == 0:
						sql_where += ""
					else:
						sql_where += "AND d.progress_tp = '%s' " % searchProgress

				if searchDamage is not None:
					sql_where += "AND d.damage_tp IN (%s) " % searchDamage

				if searchText is not None:
					sql_where += "AND (d.lat LIKE '%%%s%%' OR d.lng LIKE '%%%s%%') " % (searchText, searchText)

				# order by
				sql_order = "d.seq DESC "

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

				tblId = 'damage/images'
				damageTypeCode = '020000'
				itemList = []
				for idx, row in enumerate(cursor.fetchall()):
					item={}
					item['no'] = (total_result['cnt'] - pageSize*(page - 1) - idx)
					item['damageNo'] = row['seq']
					item['beforeImage'] = get_contents_file(row['seq'], tblId, 'before', svt)
					item['afterImage'] = get_contents_file(row['seq'], tblId, 'after', svt)
					item['lat'] = row['lat']
					item['lng'] = row['lng']
					item['damageTp'] = row['damage_tp']
					item['damageNm'] = row['damageNm']
					item['progressTp'] = row['progress_tp']
					item['progressNm'] = row['progressNm']
					# item['used'] = row['used']
					# if row['used'] == '1':
					# 	item['usedNm'] = '사 용'
					# else:
					# 	item['usedNm'] = '중 지'
					item['memo'] = row['memo']

					if row['insert_dt'] is not None:
						item['insertDt'] = row['insert_dt'].strftime("%Y-%m-%d")
					else:
						item['insertDt'] = ''

					if row['end_dt'] is not None:
						item['endDt'] = row['end_dt'].strftime("%Y-%m-%d")
					else:
						item['endDt'] = ''
					itemList.append(item)

				# 도로 파손 코드 정보
				data['damageTypeList'] = get_common_code_list(damageTypeCode, 1, svt)

				# 진행 상태
				progressCode = '030000'
				data['progressList'] = get_common_code_list(progressCode, 1, svt)

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

