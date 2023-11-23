# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
from werkzeug.datastructures import FileStorage
import datetime
from src.common.function import *

PjDamage = Namespace('PjDamage')

PjDamageGet = PjDamage.schema_model('PjDamageGet', {
})
PjDamagePost = PjDamage.schema_model('PjDamagePost', {
})
PjDamagePut = PjDamage.schema_model('PjDamagePut', {
})
PjDamageDelete = PjDamage.schema_model('PjDamageDelete', {
})
@PjDamage.route('', methods=['GET','POST','PUT','DELETE'])
class PjDamageApi(Resource):
	####################################################################################################################
	# METHOD : GET
	# write  : 23.08.25
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = PjDamage.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('damageNo', type=int, required=True, location='body', help='판매점 번호')
	@PjDamage.expect(swagger)

	@PjDamage.doc(model=PjDamageGet)

	def get(self):
		"""
		데이터 VIEW
		필수 : Authorization, damageNo
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
		parser=reqparse.RequestParser()
		parser.add_argument('damageNo', type=str, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		cursor = mysql_cursor(mysql_conn(svt))

		try:
			hasParam = True

			if 'damageNo' not in parameter or not parameter['damageNo']:
				hasParam = False

			if hasParam :
				damageNo = parameter['damageNo']

				tblId = 'damage/images'


				sql = """
					SELECT
						d.lat,
						d.lng,
						d.damage_tp,
						d.progress_tp,
						d.end_dt,
						d.insert_dt,
						d.memo
					FROM
						pj_damage d
					WHERE
						d.seq = %s
				"""
				cursor.execute(query=sql, args=damageNo)
				row = cursor.fetchone()

				data['lat'] = row['lat']
				data['lng'] = row['lng']
				data['damageTp'] = row['damage_tp']
				data['progressTp'] = row['progress_tp']
				data['damageTypeList'] = get_common_code_list('020000', 1, svt)
				if row['insert_dt'] is not None:
					data['enterDt'] = row['insert_dt'].strftime('%Y-%m-%d')
				else:
					data['enterDt'] = ''
				if row['end_dt'] is not None:
					data['endDt'] = row['end_dt'].strftime('%Y-%m-%d')
				else:
					data['endDt'] = ''

				data['memo'] = row['memo']
				data['beforeFile'] = get_contents_file(damageNo, tblId, 'before', svt)
				data['afterFile'] = get_contents_file(damageNo, tblId, 'after', svt)

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


	####################################################################################################################
	# METHOD : POST
	# write  : 23.08.25
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = PjDamage.parser()
	swagger.add_argument('Authorization', required=True,  location='headers', help='로그인토큰')
	swagger.add_argument('lat',           required=True,  type=str, location='body', help='위도')
	swagger.add_argument('lng',           required=True,  type=str, location='body', help='경도')
	swagger.add_argument('damageTp',      required=True,  type=str, location='body', help='파손종류')
	swagger.add_argument('progressTp',    required=True,  type=int, location='body', help='진행상태')
	swagger.add_argument('beforeFile',    required=False, type=FileStorage, location='files', help='등록이미지')
	swagger.add_argument('afterFile',     required=False, type=FileStorage, location='files', help='완료이미지')
	swagger.add_argument('memo',          required=False, type=str, location='body', help='메모')
	# swagger.add_argument('used',          required=True,  type=int, location='body', help='사용유무')
	@PjDamage.expect(swagger)

	@PjDamage.doc(model=PjDamagePost)

	def post(self):
		"""
		도로 파손 정보 등록
		필수 : Authorization, lat, lng, damageTp, progressTp
		일반 : beforeFile, afterFile, memo
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
		parser.add_argument('lat',        required=True,  type=str)
		parser.add_argument('lng',        required=True,  type=str)
		parser.add_argument('damageTp',   required=True,  type=str)
		parser.add_argument('progressTp', required=True,  type=int)
		parser.add_argument('beforeFile', required=False, type=FileStorage)
		parser.add_argument('afterFile',  required=False, type=FileStorage)
		parser.add_argument('memo',       required=False, type=str)
		# parser.add_argument('used',       required=True,  type=int)
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True

			if 'lat' not in parameter or not parameter['lat']:
				hasParam = False

			if 'lng' not in parameter or not parameter['lng']:
				hasParam = False

			if 'damageTp' not in parameter or not parameter['damageTp']:
				hasParam = False

			if 'progressTp' not in parameter or not parameter['progressTp']:
				hasParam = False

			# if 'used' not in parameter or not parameter['used']:
			# 	hasParam = False

			if hasParam :

				lat = parameter['lat']
				lng = parameter['lng']
				damageTp = parameter['damageTp']
				progressTp = parameter['progressTp']
				# used = parameter['used']

				beforeFile = None
				if 'beforeFile' in request.files:
					beforeFile = request.files['beforeFile']

				afterFile = None
				if 'afterFile' in request.files:
					afterFile = request.files['afterFile']

				memo = None
				if 'memo' in parameter and parameter['memo'] != '':
					memo = parameter['memo']

				# transation 시작
				conn.begin()
				try:

					# 등록
					sql = """
						INSERT INTO pj_damage(lat, lng, damage_tp, progress_tp, memo, insert_id, insert_ip)
						VALUES(%s, %s, %s, %s, %s, %s, %s)
					"""
					cursor.execute(query=sql, args=(lat, lng, damageTp, progressTp, memo, payload['userId'], userIp))
					data['damageNo'] = cursor.lastrowid

					# 첨부파일 - 이미지
					beforeData = None
					if beforeFile is not None:
						tblId = 'damage/images'
						tblType = 'before'
						thumbYn = 'N'
						beforeData = fileUpload(beforeFile, tblId, tblType, thumbYn, svt)

					if beforeData is not None:
						# print('fileData >> ', fileData)
						sql = """
						INSERT INTO sy_file(tbl_seq, tbl_id, tbl_type, file_name, file_name_origin, file_path, file_path_thumb, file_type, file_size, insert_id, insert_ip)
						VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
						"""
						cursor.execute(query=sql, args=(data['damageNo'], tblId, tblType, beforeData['fileName'], beforeData['fileNameOrigin'], beforeData['fileFullPath'], beforeData['filePathThumb'], beforeData['fileType'], beforeData['fileSize'], payload['userId'], userIp))

					afterData = None
					if afterFile is not None:
						tblId = 'damage/images'
						tblType = 'after'
						thumbYn = 'N'
						afterData = fileUpload(afterFile, tblId, tblType, thumbYn, svt)

					if afterData is not None:
						# print('fileData >> ', fileData)
						sql = """
						INSERT INTO sy_file(tbl_seq, tbl_id, tbl_type, file_name, file_name_origin, file_path, file_path_thumb, file_type, file_size, insert_id, insert_ip)
						VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
						"""
						cursor.execute(query=sql, args=(data['damageNo'], tblId, tblType, afterData['fileName'], afterData['fileNameOrigin'], afterData['fileFullPath'], afterData['filePathThumb'], afterData['fileType'], afterData['fileSize'], payload['userId'], userIp))

				except Exception as e:
					conn.rollback()
					raise

				else:
					conn.commit()


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
	# write  : 23.08.25
	# writer : chside
	####################################################################################################################
	# swagger 파라미터
	swagger = PjDamage.parser()
	swagger.add_argument('Authorization', required=True,  location='headers', help='로그인토큰')
	swagger.add_argument('damageNo',      required=True,  type=int, location='body', help='pj_damage.seq')
	swagger.add_argument('lat',           required=True,  type=str, location='body', help='위도')
	swagger.add_argument('lng',           required=True,  type=str, location='body', help='경도')
	swagger.add_argument('damageTp',      required=True,  type=str, location='body', help='파손종류')
	swagger.add_argument('progressTp',    required=True,  type=int, location='body', help='진행상태')
	swagger.add_argument('endDt',    	  required=False, type=str, location='body', help='완료일')
	swagger.add_argument('beforeFile',    required=False, type=FileStorage, location='files', help='등록이미지')
	swagger.add_argument('afterFile',     required=False, type=FileStorage, location='files', help='완료이미지')
	swagger.add_argument('memo',          required=False, type=str, location='body', help='메모')
	# swagger.add_argument('used',          required=True,  type=int, location='body', help='사용유무')

	@PjDamage.expect(swagger)

	@PjDamage.doc(model=PjDamagePut)

	def put(self):
		"""
		회원정보 수정
		필수 : Authorization, damageNo, lat, lng, damageTp, progressTp, used
		일반 : endDt, beforeFile, afterFile, memo
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
		parser.add_argument('damageNo',   required=True,  type=int)
		parser.add_argument('lat',        required=True,  type=str)
		parser.add_argument('lng',        required=True,  type=str)
		parser.add_argument('damageTp',   required=True,  type=str)
		parser.add_argument('progressTp', required=True,  type=int)
		parser.add_argument('endDt', 	  required=False, type=str)
		parser.add_argument('beforeFile', required=False, type=FileStorage)
		parser.add_argument('afterFile',  required=False, type=FileStorage)
		parser.add_argument('memo',       required=False, type=str)
		# parser.add_argument('used',       required=True,  type=int)
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True
			if 'damageNo' not in parameter or not parameter['damageNo']:
				hasParam = False

			if 'lat' not in parameter or not parameter['lat']:
				hasParam = False

			if 'lng' not in parameter or not parameter['lng']:
				hasParam = False

			if 'damageTp' not in parameter or not parameter['damageTp']:
				hasParam = False

			if 'progressTp' not in parameter or not parameter['progressTp']:
				hasParam = False

			# if 'used' not in parameter or not parameter['used']:
			# 	hasParam = False

			if hasParam :
				damageNo = parameter['damageNo']
				lat = parameter['lat']
				lng = parameter['lng']
				damageTp = parameter['damageTp']
				progressTp = parameter['progressTp']
				# used = parameter['used']

				if progressTp == 9:
					if 'endDt' in parameter and parameter['endDt'] != '':
						endDt = parameter['endDt']
					else:
						endDt = None
				else:
					endDt = None

				beforeFile = None
				if 'beforeFile' in request.files:
					beforeFile = request.files['beforeFile']

				afterFile = None
				if 'afterFile' in request.files:
					afterFile = request.files['afterFile']

				memo = None
				if 'memo' in parameter and parameter['memo'] != '':
					memo = parameter['memo']

				today = datetime.datetime.now()

				sql = "SELECT * FROM pj_damage WHERE seq = %s "
				cursor.execute(query=sql, args=damageNo)
				result = cursor.fetchone()

				if result is not None:
					# transation 시작
					conn.begin()
					try:

						sql = """
							UPDATE pj_damage SET
								lat = %s,
								lng = %s,
								damage_tp = %s,
								progress_tp = %s,
								end_dt = %s,
								memo = %s,
								update_id = %s,
								update_ip = %s
							WHERE
								seq = %s
						"""
						cursor.execute(query=sql, args=(lat, lng, damageTp, progressTp, endDt, memo, payload['userId'], userIp, damageNo))

						# 첨부파일 - 등록 이미지
						beforeData = None
						if beforeFile is not None:
							tblId = 'damage/images'
							tblType = 'before'
							thumbYn = 'N'
							beforeData = fileUpload(beforeFile, tblId, tblType, thumbYn, svt)

						if beforeData is not None:
							# print('fileData >> ', fileData)
							sql = """
							UPDATE sy_file SET
								delete_id = %s, delete_dt = %s, delete_ip = %s
							WHERE
								tbl_seq = %s AND tbl_id = %s AND tbl_type = %s AND delete_id IS NULL
							"""
							cursor.execute(query=sql, args=(payload['userId'], today, userIp, damageNo, tblId, tblType))

							sql = """
							INSERT INTO sy_file(tbl_seq, tbl_id, tbl_type, file_name, file_name_origin, file_path, file_path_thumb, file_type, file_size, insert_id, insert_ip)
							VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
							"""
							cursor.execute(query=sql, args=(damageNo, tblId, tblType, beforeData['fileName'], beforeData['fileNameOrigin'], beforeData['fileFullPath'], beforeData['filePathThumb'], beforeData['fileType'], beforeData['fileSize'], payload['userId'], userIp))


						afterData = None
						if afterFile is not None:
							tblId = 'damage/images'
							tblType = 'after'
							thumbYn = 'N'
							afterData = fileUpload(afterFile, tblId, tblType, thumbYn, svt)

						if afterData is not None:
							# print('fileData >> ', fileData)
							sql = """
							UPDATE sy_file SET
								delete_id = %s, delete_dt = %s, delete_ip = %s
							WHERE
								tbl_seq = %s AND tbl_id = %s AND tbl_type = %s AND delete_id IS NULL
							"""
							cursor.execute(query=sql, args=(payload['userId'], today, userIp, damageNo, tblId, tblType))

							sql = """
							INSERT INTO sy_file(tbl_seq, tbl_id, tbl_type, file_name, file_name_origin, file_path, file_path_thumb, file_type, file_size, insert_id, insert_ip)
							VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
							"""
							cursor.execute(query=sql, args=(damageNo, tblId, tblType, afterData['fileName'], afterData['fileNameOrigin'], afterData['fileFullPath'], afterData['filePathThumb'], afterData['fileType'], afterData['fileSize'], payload['userId'], userIp))

						data['damageNo'] = damageNo

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
	swagger = PjDamage.parser()
	swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
	swagger.add_argument('damageNo', required=True, type=int, location='body', help='pjDamage.seq')
	@PjDamage.expect(swagger)

	@PjDamage.doc(model=PjDamageDelete)

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
		parser.add_argument('damageNo', type=int, required=True, location='args')
		parameter = parser.parse_args()

		# DB 시작
		# cursor = mysql_cursor(mysql_conn(svt))
		conn = mysql_conn(svt)
		cursor = mysql_cursor(conn)

		try:
			hasParam = True

			if 'damageNo' not in parameter or not parameter['damageNo']:
				hasParam = False

			if hasParam :
				damageNo = parameter['damageNo']

				sql = "SELECT * FROM pj_damage WHERE seq = %s AND delete_id IS NULL"
				cursor.execute(query=sql, args=damageNo)
				result = cursor.fetchone()

				if result is not None:

					today = datetime.datetime.now()
					# transation 시작
					conn.begin()
					try:
						sql = """
						UPDATE pj_damage SET
							delete_id=%s, delete_dt=%s, delete_ip=%s
						WHERE seq=%s
						"""
						cursor.execute(query=sql, args=(payload['userId'], today, userIp, damageNo))

						# 첨부파일 - 이미지
						tblId = 'damage/images'
						tblType = 'before'

						sql = """
						UPDATE sy_file SET
							delete_id = %s, delete_dt = %s, delete_ip = %s
						WHERE
							tbl_seq = %s AND delete_id IS NULL
						"""
						cursor.execute(query=sql, args=(payload['userId'], today, userIp, damageNo))



					except Exception as e:
						conn.rollback()
						raise

					else:
						conn.commit()

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
