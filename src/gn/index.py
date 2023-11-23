# -*- coding: utf-8 -*-
import logging
from os import stat
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

GnIndex = Namespace('GnIndex')

GnIndexGet = GnIndex.schema_model('GnIndexGet', {

})

@GnIndex.route('', methods=['GET'])
class GnIndexApi(Resource):

	swagger = GnIndex.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('pageId', required=False, location='body', help='로그인토큰')
	@GnIndex.expect(swagger)

	@GnIndex.doc(model=GnIndexGet)

	def get(self):
		"""
		관리자 Index
		필수 : Authorization
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
			data['error'] = '권한이 없습니다'
			return data, 401

		# 파라미터 정리
		parser = reqparse.RequestParser()
		parser.add_argument('pageId', type=str, required=False, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:

			hasParam = True

			if hasParam :

				startDt = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
				endDt = datetime.datetime.now().strftime("%Y-%m-%d")

				data['startDt'] = startDt
				data['endDt'] = endDt

				# 일별 파손 등록 건
				data['dailyDamageLabel'], data['dailyDamageQty'] = get_graph_daily_damage(svt)

				# 도로 파손 코드 정보
				damageTypeCode = '020000'
				data['damageTypeList'] = get_common_code_list(damageTypeCode, 1, svt)

				# 전체 및 최근 등록 수
				data['total'], data['yesterday'], data['today'] = get_damage_stat(svt)

				# 파손 종류 별 등록 수
				data['totalDamageList'] = get_total_damage_stat(svt)

				# 진행 상태 별 등록 수
				data['totalProgressList'] = get_total_progress_stat(svt)

				# 최근 등록 건수
				sql = """
					SELECT
						d.seq,
						d.lat,
						d.lng,
						d.damage_tp,
						d.progress_tp,
						(SELECT code_name FROM sy_common WHERE parent_id = '030000' AND code_step = 2 AND code_value = d.progress_tp) AS progressNm,
						d.insert_dt,
						d.memo
					FROM
						pj_damage d
					WHERE
						d.delete_id IS NULL
					ORDER BY
						d.seq DESC
					LIMIT
						7
				"""
				cursor.execute(query=sql)
				tblId = 'damage/images'
				tblTp = 'before'
				damageTypeCode = '020000'
				itemList = []
				for idx, row in enumerate(cursor.fetchall()):
					item={}
					item['damageNo'] = row['seq']
					item['listImage'] = get_contents_file(row['seq'], tblId, tblTp, svt)
					item['lat'] = row['lat']
					item['lng'] = row['lng']
					item['damageTp'] = row['damage_tp']
					item['damageTpList'] = get_damage_type_list(damageTypeCode, row['damage_tp'], svt)
					item['progressTp'] = row['progress_tp']
					item['progressNm'] = row['progressNm']
					if row['insert_dt'] is not None:
						item['insertDt'] = row['insert_dt'].strftime("%Y-%m-%d")
					else:
						item['insertDt'] = ''

					itemList.append(item)
				data['damageList'] = itemList

				# print(data)

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





