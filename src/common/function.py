import pymysql
import datetime
from secrets import token_bytes
from base64 import b64encode
# import paho.mqtt.client as mqtt
import jwt  # PyJWT
from PIL import Image

import copy, uuid, pathlib, os, re, json

from src.common.config import *


def get_server_type(request):
	host = request.headers.get('Host')

	host_split = host.split('.')
	st = host_split[0]
	ip = request.remote_addr
	return st, host, ip


####################################################################################################################
# DATABASE 생성
####################################################################################################################
# DB에 접속하고 커서를 반환한다.
def mysql_conn(svt=''):
	if svt == '192' or svt == '106':
		# 개발
		host = MySqlConfig.HOST  # api 주소
		port = MySqlConfig.PORT
		db_name = MySqlConfig.DATABASE
		user = MySqlConfig.USER
		password = MySqlConfig.PASSWORD

	else:
		# 운영
		host = MySqlConfig.HOST_PRODUCT
		port = MySqlConfig.PORT_PRODUCT
		db_name = MySqlConfig.DATABASE_PRODUCT
		user = MySqlConfig.USER_PRODUCT
		password = MySqlConfig.PASSWORD_PRODUCT

	conn = pymysql.connect(host = host, port = port, user = user, password = password, db = db_name, charset = 'utf8mb4', autocommit = True)
	return conn

def mysql_cursor(conn):
	curs = conn.cursor(pymysql.cursors.DictCursor)
	return curs


def get_fetchOne(field, table, where, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))
	sql = " SELECT %s FROM %s WHERE %s " %(field, table, where)
	cursor.execute(query = sql)
	item = cursor.fetchone()

	# DB 종료
	cursor.close()
	return item

def get_fetchAll(field, table, where, order, limit, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	if limit is not None:
		sql = f" SELECT {field} FROM {table} WHERE {where} ORDER BY {order} Limit {limit} "
	else:
		sql = f" SELECT {field} FROM {table} WHERE {where} ORDER BY {order} "

	cursor.execute(query=sql)
	item = cursor.fetchall()

	# DB 종료
	cursor.close()

	return item


def get_total_page(totalCount, pageSize):
# 페이지 수 계산
	if totalCount % pageSize == 0:
		return totalCount // pageSize
	else:
		return totalCount // pageSize + 1


####################################################################################################################
# 토큰 생성
####################################################################################################################
# 인증토큰을 생성
def jwt_token_generator(seq, userName, userId, role):
	issuer = 'shh'
	subject = 'www.gnict.co.kr'
	date_time_obj = datetime.datetime
	exp_time = date_time_obj.timestamp(date_time_obj.now() + datetime.timedelta(hours=24))

	if role == 2:
		roleText = '회원'
	elif role == 5:
		roleText = '직원'
	elif role == 9:
		roleText = '관리자'
	else:
		roleText = ''

	payload = {
		'userNo': seq,
		'userName': userName,
		'userId': userId,
		'role': role,
		'roleText': roleText,
		'sub': subject,
		'iss': issuer,
		'exp': int(exp_time)
	}

	return jwt.encode(payload, JWTConfig.SECRET, algorithm = 'HS256')


def jwt_refresh_token_generator(seq):
	date_time_obj = datetime.datetime
	refresh_payload = {
		'seq': seq,
		'exp': date_time_obj.timestamp(date_time_obj.now() + datetime.timedelta(days=15))
	}
	return jwt.encode(refresh_payload, JWTConfig.SECRET, algorithm = 'HS256')



def decode_jwt(headers):
	try:
		if 'Authorization' in headers:
			access_token = headers['Authorization'].replace('Bearer ', '')

			if access_token:
				try:
					payload = jwt.decode(access_token, JWTConfig.SECRET, algorithms = "HS256")

				except jwt.InvalidTokenError:
					payload = None

				if payload is not None:
					exp = int(payload['exp'])
					date_time_obj = datetime.datetime
					now_time = int(date_time_obj.timestamp(date_time_obj.now()))

					# 만기 시간이 더 크면 사용할 수 있는 토큰임
					if exp > now_time:
						return payload

		return None
	except BaseException:
		return None


#  openssl rand -base64 32 생성
def get_rand_base64_token():
	return b64encode(token_bytes(32)).decode()



####################################################################################################################
# System 일반
####################################################################################################################

def json_null_to_empty(x):
	# return 시 null -> '' 변환
	ret = copy.deepcopy(x)

	if isinstance(x, dict):

		for k, v in ret.items():
			ret[k] = json_null_to_empty(v)

	if isinstance(x, (list, tuple)):

		for k, v in enumerate(ret):
			ret[k] = json_null_to_empty(v)

	if x is None:
		ret = ''

	return ret


# def makeJsonMenu(svt):

# 	 # DB 시작
# 	cursor = mysql_cursor(mysql_conn(svt))

# 	#  메뉴
# 	if svt == '59':
# 		# 운영
# 		filePath = '../admin/src/assets/json/menu_cms.json'
# 	elif svt == '106':
# 		# 개발서버
# 		filePath = '../admin/src/assets/json/menu_cms.json'
# 	else:
# 		# local
# 		filePath = '../web/src/assets/json/menu_cms.json'

# 	sql = """
# 	SELECT
# 		menu_id, parent_id, menu_step, menu_name, menu_type, menu_sort, menu_url, used
# 	FROM
# 		sy_menu
# 	WHERE
# 		menu_step = 1 AND delete_id IS NULL AND used = '1'
# 	ORDER BY
# 		menu_id, menu_sort ASC
# 	"""
# 	cursor.execute(query=sql)

# 	itemList = []
# 	for row in cursor.fetchall():
# 		item = {}
# 		item['menuUrl'] = ''
# 		if row['menu_url'] != '' or row['menu_url'] is not None:
# 			item['menuUrl'] = row['menu_url']

# 		item['menuId'] = row['menu_id']
# 		item['menuName'] = row['menu_name']
# 		item['parentId'] = row['parent_id']
# 		item['menuStep'] = row['menu_step']
# 		item['menuSort'] = row['menu_sort']
# 		item['menuType'] = row['menu_type']
# 		item['used'] = row['used']
# 		item['active'] = ''
# 		item['menuSub'] = get_sub_menu(row['menu_id'], '1', '', svt)
# 		itemList.append(item)


# 	# DB 종료
# 	cursor.close()



def get_sub_menu(menuId, used, role, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	sql = """
		SELECT
			menu_id, parent_id, menu_step, menu_name, menu_type, menu_sort, menu_url, menu_icon, menu_role, used
		FROM sy_menu
		WHERE delete_id IS NULL AND parent_id = %s AND menu_step = 2 """ % menuId
	if used == '1':
		sql = sql + "AND used = '1' "

	sql = sql + "ORDER BY menu_sort, menu_id ASC"
	cursor.execute(query=sql)

	itemList = []
	for row in cursor.fetchall():
		item={}
		item['active'] = ""
		item['menuId'] = row['menu_id']
		item['parentId'] = row['parent_id']
		item['menuName'] = row['menu_name']
		item['menuStep'] = row['menu_step']
		item['menuSort'] = row['menu_sort']
		item['menuType'] = row['menu_type']
		item['menuUrl'] = row['menu_url']
		item['menuIcon'] = row['menu_icon']
		item['menuRole'] = row['menu_role']
		item['used'] = row['used']
		itemList.append(item)

	# DB 종료
	cursor.close()

	return itemList


def get_common_code_list(parentId, use, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	# sql = "SELECT * FROM sy_code WHERE parent_id = '%s' AND code_step = 2 " % parentId
	sql = """
		SELECT
			*
		FROM
			sy_common
		WHERE
			parent_id = %s AND code_step = 2 """ % parentId
	if use == 1:
		sql += "AND used = %s " % use

	sql += "ORDER BY code_sort ASC "
	cursor.execute(query=sql)

	itemList = []
	for row in cursor.fetchall():
		item = {}
		item['codeId'] = row['code_id']
		item['parentId'] = row['parent_id']
		item['codeName'] = row['code_name']
		item['codeValue'] = row['code_value']
		item['codeStep'] = row['code_step']
		item['codeSort'] = row['code_sort']
		item['used'] = row['used']
		if parentId == '020000':
			if svt == '192':
				fileFullPath = FileUrl.Local + 'static/files/damage-' + str(row['code_value']) + '.png'
			else:
				fileFullPath = FileUrl.Server + 'static/files/damage-' + str(row['code_value']) + '.png'
			item['markerIcon'] = fileFullPath

		itemList.append(item)

	# DB 종료
	cursor.close()
	return itemList


####################################################################################################################
# 파일
####################################################################################################################
def get_file_ext(source):
	source_arr = source.split(".")
	return source_arr[len(source_arr) - 1].lower()


def get_file_name(file_name):
	return file_name[:file_name.rfind(".")]


def fileUpload(upFile, tblId, tblType, thumbYn, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	# 원본 파일명
	fileNameOrigin = upFile.filename

	# 저장될 파일 이름 변경
	fileName = str(uuid.uuid4()) + pathlib.Path(fileNameOrigin).suffix

	# 파일타입
	fileType = upFile.content_type

	# 파일 확장자
	ext = get_file_ext(fileNameOrigin)

	# 파일 경로
	if svt == '192':
		# win
		filePath = FilePath.fileDir
	else:
		# linux
		filePath = FilePath.rootDir + FilePath.fileDir

	fileDetailPath = ''
	if tblId != '' and tblId is not None:
		fileDetailPath += tblId + '/'

	# if tblType != '' and tblType is not None:
	# 	fileDetailPath += tblType + '/'

	# 파일 전체 경로
	fileFullPath = filePath + fileDetailPath + fileName
	saveFileFullPath = FilePath.fileDir + fileDetailPath + fileName

	# 저장 폴더 설정
	fileFullDir = filePath + fileDetailPath
	dirTp = os.path.isdir(fileFullDir)
	# print('fileFullDir >>', fileFullDir, dirTp)
	if dirTp == False:
		os.mkdir(fileFullDir)

	# 파일저장
	upFile.save(fileFullPath)
	fileSize = os.path.getsize(fileFullPath)
	# in_memory_uploaded_file = upFile.read()
	# fileSize = len(in_memory_uploaded_file)

	filePathThumb = None
	if thumbYn=='Y' and (ext == 'jpg' or ext == 'gif' or ext == 'png'):
		# 섬네일 생성
		tmp_file_name = os.path.basename(fileFullPath)
		thumbFileName = get_file_name(tmp_file_name) + '_thumb.' + ext

		filePathThumb = filePath + fileDetailPath + thumbFileName

		thumb = Image.open(fileFullPath)
		orizin_width, orizin_height = thumb.size
		width = 600
		height = int((width*orizin_height) / orizin_width)

		size = (int(width), int(height))
		thumb.thumbnail(size)
		thumb.save(filePathThumb)
		# root 경로 제거
		filePathThumb = FilePath.fileDir + fileDetailPath + thumbFileName

	# sql = """
	# INSERT INTO sy_file(tbl_seq, tbl_id, tbl_type, file_name, file_name_origin, file_path, file_path_thumb, file_type, file_size, insert_id, insert_ip)
	# VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
	# cursor.execute(query=sql, args=(tblSeq, tblId, tblType, fileName, fileNameOrigin, fileFullPath, filePathThumb, fileType, fileSize, payload['userId'], userIp))
	# seq = cursor.lastrowid
	item = {'fileNameOrigin':fileNameOrigin, 'fileName':fileName, 'fileFullPath':saveFileFullPath, 'filePathThumb':filePathThumb, 'fileType':fileType, 'fileSize':fileSize, 'tblId':tblId}

	# DB 종료
	cursor.close()

	return item


def get_contents_file_list(seq, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	sql = """
	SELECT
		tbl_seq,
		tbl_id,
		tbl_type,
		file_name,
		file_name_origin,
		file_path,
		file_path_thumb,
		file_size,
		file_type
	FROM
		sy_file
	WHERE
		tbl_seq = %s
	ORDER BY
		seq ASC
	"""
	cursor.execute(query=sql, args=seq)
	itemList = []
	for row in cursor.fetchall():
		item = {}
		item['tblSeq'] = row['tbl_seq']
		item['tblId'] = row['tbl_id']
		item['tblType'] = row['tbl_type']
		item['fileName'] = row['file_name']
		item['fileNameOrigin'] = row['file_name_origin']

		filePath = ''
		if svt == '192':

			if row['file_path'] is not None:
				filePath = row['file_path']
				chkIsFile = os.path.isfile(filePath)

				if chkIsFile:
					item['filePath'] = FileUrl.Local + row['file_path']
				else:
					item['filePath'] = ''

			else:
				item['filePath'] = ''

			# if row['file_path_thumb'] is not None:
			# 	item['filePathThumb'] = FileUrl.Local + row['file_path_thumb']
			# else:
			# 	item['filePathThumb'] = ''
		else:
			if row['file_path'] is not None:
				filePath = FileUrl.Server + row['file_path']
				chkIsFile = os.path.isfile(filePath)
				if chkIsFile:
					item['filePath'] = FileUrl.Server + row['file_path']
				else:
					item['filePath'] = ''


			else:
				item['filePath'] = ''

			# if row['file_path_thumb'] is not None:
			# 	item['filePathThumb'] = FileUrl.Server + row['file_path_thumb']
			# else:
			# 	item['filePathThumb'] = ''

		item['fileSize'] = row['file_size']
		item['fileType'] = row['file_type']
		itemList.append(item)

	# DB 종료
	cursor.close()
	return itemList


def get_contents_file(seq, tid, tp, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	sql = """
	SELECT
		tbl_seq,
		tbl_id,
		tbl_type,
		file_name,
		file_name_origin,
		file_path,
		file_path_thumb,
		file_size,
		file_type
	FROM
		sy_file
	WHERE
		delete_id IS NULL
		AND tbl_seq = %s
		AND tbl_id = %s
		AND tbl_type = %s
	ORDER BY
		seq ASC
	LIMIT 1
	"""
	cursor.execute(query=sql, args=(seq, tid, tp))
	res = cursor.fetchone()

	if res is not None:
		if svt == '192':
			isFilePath = res['file_path']
			fileFullPath = FileUrl.Local

		else:
			isFilePath = FilePath.rootDir + res['file_path']
			fileFullPath = FileUrl.Server

		chkIsFile = os.path.isfile(isFilePath)

		if chkIsFile:
			item = {}
			item['tblSeq'] = res['tbl_seq']
			item['tblId'] = res['tbl_id']
			item['tblType'] = res['tbl_type']
			item['fileName'] = res['file_name']
			item['fileNameOrigin'] = res['file_name_origin']
			item['filePath'] = fileFullPath + res['file_path']
			item['fileSize'] = res['file_size']
			item['fileType'] = res['file_type']
		else:
			item = ''
	else:
		item = ''

	# DB 종료
	cursor.close()
	return item


####################################################################################################################
# 통계
####################################################################################################################
def get_graph_daily_damage(svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	# datasets = [
	# 	{
	# 		'label': '포트홀',
	# 		'data': [1, 2, 3, 4, 5, 6, 7],
	# 		'backgroundColor': 'rgba(54, 162, 235)',
	# 		'borderColor': 'rgb(54, 162, 235)',
	# 	},
	# ]

	now = datetime.datetime.now()
	label = []
	datasets = []

	sql = """
		SELECT * FROM sy_common
		WHERE parent_id = '020000' AND code_step = 2 AND used = 1 AND delete_id IS NULL
		ORDER BY code_sort ASC
	"""
	cursor.execute(query=sql)

	for idx, row in enumerate(cursor.fetchall()):
		item = {}
		item['label'] = row['code_name']
		item['data'] = []
		datasets.append(item)

	for i in range(7, 0, -1):
		date = (now - datetime.timedelta(days=i-1)).strftime("%Y-%m-%d")
		dt = (now - datetime.timedelta(days=i-1)).strftime("%m-%d")

		label.append(dt)

		# 일별 등록 건수
		sql = """
			SELECT
				c.code_name
				, c.code_value
				, COUNT(d.damage_tp) damageCnt
			FROM
				sy_common c
				LEFT JOIN (
					SELECT damage_tp
					FROM pj_damage
					WHERE
						delete_id IS NULL
						AND DATE_FORMAT(insert_dt, '%%Y-%%m-%%d') = %s
				) AS d ON d.damage_tp = c.code_value

			WHERE
				c.parent_id = '020000'
				AND c.code_step = 2
				AND c.used = 1
				AND c.delete_id IS NULL
			GROUP BY
				c.code_name, c.code_value
			ORDER BY
				c.code_value  ASC
		"""
		cursor.execute(query=sql, args=date)


		for idx, row in enumerate(cursor.fetchall()):
			if datasets[idx]['label'] == row['code_name']:
				datasets[idx]['data'].append(row['damageCnt'])

	# DB 종료
	cursor.close()
	return label, datasets


def get_damage_stat(svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	startDt = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
	endDt = datetime.datetime.now().strftime("%Y-%m-%d")

	total = 0
	yester = 0
	today = 0

	sql = "SELECT COUNT(*) AS cnt FROM pj_damage WHERE delete_id IS NULL "
	cursor.execute(query=sql)
	result = cursor.fetchone()
	total = result['cnt']

	sql = "SELECT COUNT(*) AS cnt FROM pj_damage WHERE delete_id IS NULL AND DATE_FORMAT(insert_dt, '%%Y-%%m-%%d') = %s "
	cursor.execute(query=sql, args=startDt)
	yresult = cursor.fetchone()
	yester = yresult['cnt']

	sql = "SELECT COUNT(*) AS cnt FROM pj_damage WHERE delete_id IS NULL AND DATE_FORMAT(insert_dt, '%%Y-%%m-%%d') = %s "
	cursor.execute(query=sql, args=endDt)
	sresult = cursor.fetchone()
	today = sresult['cnt']

	# DB 종료
	cursor.close()

	return total, yester, today


def get_graph_order_count(seq, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	now = datetime.datetime.now()
	label = []
	qty = []

	for i in range(7, 0, -1):
		date = (now - datetime.timedelta(days=i-1)).strftime("%Y-%m-%d")
		dt = (now - datetime.timedelta(days=i-1)).strftime("%m-%d")

		# 기간별 주문 건수
		# sql = "SELECT COUNT(*) AS cnt FROM sa_reserve WHERE store = %s AND reserve_dt = %s"
		sql = "SELECT COUNT(*) AS cnt FROM pj_order WHERE seq = %s AND reserve_dt = %s"
		cursor.execute(query=sql, args=(seq, date))
		result = cursor.fetchone()

		# 기간별 주문 품목


		label.append(dt)
		qty.append(result['cnt'])

	# DB 종료
	cursor.close()
	return label, qty


def get_total_damage_stat(svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	classArr = ['progress-bar-info', 'progress-bar-success', 'progress-bar-warning', 'progress-bar-danger']

	sql = """
		SELECT
			c.code_name
			, c.code_value
			, COUNT(d.damage_tp) damage_cnt
			, ROUND(COUNT(d.damage_tp) / (SELECT COUNT(*) FROM pj_damage WHERE delete_id IS NULL)*100, 2) AS damage_rate
		FROM
			sy_common c
			LEFT JOIN pj_damage d ON d.damage_tp = c.code_value
		WHERE
			c.parent_id = '020000'
			AND c.code_step = 2
			AND c.used = 1
			AND c.delete_id IS NULL AND d.delete_id IS NULL
		GROUP BY
			c.code_name, c.code_value
		ORDER BY
			c.code_value  ASC
	"""
	cursor.execute(query=sql)
	itemList = []
	for idx, row in enumerate(cursor.fetchall()):
		item = {}
		item['damageTp'] = row['code_value']
		item['damageNm'] = row['code_name']
		item['damageCount'] = row['damage_cnt']
		item['damageRate'] = int(row['damage_rate'])
		item['damageClass'] = classArr[idx]
		itemList.append(item)

	# DB 종료
	cursor.close()
	return itemList


def get_total_progress_stat(svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))
	classArr = ['progress-bar-info', 'progress-bar-primary', 'progress-bar-danger']

	sql = """
		SELECT
			c.code_name
			, c.code_value
			, COUNT(d.progress_tp) progress_cnt
			, ROUND(COUNT(d.progress_tp) / (SELECT COUNT(*) FROM pj_damage WHERE delete_id IS NULL)*100, 2) AS progress_rate
		FROM
			sy_common c
			LEFT JOIN pj_damage d ON d.progress_tp = c.code_value
		WHERE
			c.parent_id = '030000'
			AND c.code_step = 2
			AND c.used = 1
			AND c.delete_id IS NULL AND d.delete_id IS NULL
		GROUP BY
			c.code_name, c.code_value
		ORDER BY
			c.code_value  ASC
	"""
	cursor.execute(query=sql)
	itemList = []
	for idx, row in enumerate(cursor.fetchall()):
		item = {}
		item['progressTp'] = row['code_value']
		item['progressNm'] = row['code_name']
		item['progressCount'] = row['progress_cnt']
		item['progressRate'] = int(row['progress_rate'])
		item['progressClass'] = classArr[idx]
		itemList.append(item)

	# DB 종료
	cursor.close()
	return itemList


def get_graph_order_product_count(seq, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	startDt = (datetime.datetime.now() - datetime.timedelta(days=6)).strftime("%Y-%m-%d")
	# endDt = (datetime.datetime.now() - datetime.timedelta(days=0)).strftime("%Y-%m-%d")
	endDt = datetime.datetime.now().strftime("%Y-%m-%d")

	sql = """
	SELECT sp.store_seq, sp.product_seq, p.name AS productName,
	(CASE WHEN o.qty IS NULL THEN 0 ELSE o.qty END) AS qty
	FROM pj_store_product sp
	LEFT JOIN pj_product p ON p.seq = sp.product_seq
	LEFT JOIN (
		SELECT store, product, sum(qty) AS qty
		FROM sa_reserve
		WHERE store = %s AND (reserve_dt BETWEEN %s AND %s)
		GROUP BY store, product
	) s ON o.store = sp.store_seq AND o.product = sp.product_seq
	WHERE sp.store_seq = %s AND sp.delete_id IS NULL
	ORDER BY sp.product_seq ASC
	"""
	cursor.execute(query=sql, args=(seq, startDt, endDt, seq))

	itemList = []
	label = []
	qty = []
	for row in cursor.fetchall():
		label.append(row['productName'])
		qty.append(int(row['qty']))

	# DB 종료
	cursor.close()
	return label, qty


#######################################################################################################################
# 일반 함수
# 프로젝트별로 생성
#######################################################################################################################
def chk_input_match(in_type, in_value):
	# 정규식으로 입력값 체크
	# in_type: email, mobile
	if in_type == 'email':
		# 이메일
		chk = re.compile('^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

	elif in_type == 'mobile':
		chk = re.compile('\d{3}-\d{3,4}-\d{4}')

	elif in_type == 'tel':
		chk = re.compile('\d{3}-\d{3,4}-\d{4}')

	elif in_type == 'zipcode':
		chk = re.compile('\d{5}')

	else:
		pass

	val = chk.match(in_value)

	# 결과 리턴
	if val is not None:
		return True
	else:
		return False


def get_damage_type_list(parentId, item, svt):
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	sql = """
	SELECT
		code_id,
		code_name,
		code_sort,
		code_value
	FROM
		sy_common
	WHERE
		used = 1
		AND parent_id = '%s'
		AND code_step = 2
		AND code_value IN (%s)
	ORDER BY
		code_sort ASC
	""" % (parentId, item)
	cursor.execute(query=sql)

	itemList = []
	for row in cursor.fetchall():
		item = {}
		item['codeId'] = row['code_id']
		item['codeName'] = row['code_name']
		item['codeSort'] = row['code_sort']
		item['codeValue'] = row['code_value']
		itemList.append(item)

	# DB 종료
	cursor.close()
	return itemList


def get_receive_date(startDt, svt):
	# 예약일, 수령일 계산

	# str to date
	sdt = datetime.datetime.strptime(startDt, '%Y-%m-%d').date()
	# + 14 day
	chkDt = sdt + datetime.timedelta(days=14)

	day = 0
	cnt = 0
	for i in range(20):
		recDt = chkDt + datetime.timedelta(days=i)
		day = recDt.weekday()

		# 월0~금4
		if day < 5:
			# 공휴일
			cnt = get_holiday_chk(recDt, svt)
			if cnt < 1:
				break

	return recDt.strftime("%Y-%m-%d")


def get_holiday_chk(dt, svt):
	# 휴일, 공휴일 체크
	# DB 시작
	cursor = mysql_cursor(mysql_conn(svt))

	sql = "SELECT COUNT(*) AS cnt FROM sy_holiday WHERE holiday_dt = %s AND delete_id IS NULL"
	cursor.execute(query=sql, args=dt)
	result = cursor.fetchone()
	item = result['cnt']

	# DB 종료
	cursor.close()
	return item


# mqtt
# def mqtt_publish(topic, msg, svt):
#     # 새로운 클라이언트 생성
#     client = mqtt.Client()
#     # 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_publish(메세지 발행)
#     client.on_connect = on_connect
#     client.on_disconnect = on_disconnect
#     client.on_publish = on_publish
#     # address : localhost, port: 1883 에 연결

#     if svt == '192' or svt == '106':
#         mqtt_host = Mqtt.DEV_HOST
#     else:
#         mqtt_host = Mqtt.PDT_HOST

#     client.connect(mqtt_host, Mqtt.PORT)

#     client.loop_start()

#     client.publish(topic, msg, 1)

#     # 연결 종료
#     client.disconnect()

#     return client


# def mqtt_subscribe(topic, svt):
#     # # 새로운 클라이언트 생성
#     # client = mqtt.Client()
#     # # 콜백 함수 설정 on_connect(브로커에 접속), on_disconnect(브로커에 접속중료), on_publish(메세지 발행)
#     # client.on_connect = on_connect
#     # client.on_disconnect = on_disconnect
#     # client.on_subscribe = on_subscribe
#     # client.on_message = on_message
#     # # address : localhost, port: 1883 에 연결


#     client = mqtt.Client('subscribe') #client 오브젝트 생성
#     client.on_connect = on_connect #콜백설정
#     client.on_message = on_message #콜백설정


#     if svt == '192' or svt == '106':
#         mqtt_host = Mqtt.DEV_HOST
#     else:
#         mqtt_host = Mqtt.PDT_HOST

#     client.connect(mqtt_host, Mqtt.PORT)

#     # client.loop_start()
#     # # 메세지 발행
#     client.subscribe(topic, 1)

#     client.on_connect = on_connect


#     aa = on_message

#     client.loop_forever()

#     print('>>>> ', client.on_message)
#     # # 연결 종료
#     client.disconnect()
#     return aa


# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("on_connect : connected OK")
#     else:
#         print("on_connect : Bad connection Returned code=", rc)


# def on_disconnect(client, userdata, flags, rc=0):
#     print('on_disconnect : ', str(rc))


# def on_publish(client, userdata, mid):
#     print("on_publish : In on_pub callback mid= ", mid)


# def on_subscribe(client, userdata, mid, granted_qos):
#     print("subscribed: " + str(mid) + " " + str(granted_qos))


# def on_message(client, userdata, msg):
#     # print(str('on_message : ', msg.payload.decode("utf-8")))
#     print('on_message : ', str(msg.payload.decode("utf-8")))
#     return str(msg.payload.decode("utf-8"))


# def connect_mqtt() -> mqtt:
#     def on_connect(client, userdata, flags, rc):
#         if rc == 0:
#             print("Connected to MQTT Broker")
#         else:
#             print(f"Failed to connect, Returned code: {rc}")

#     def on_disconnect(client, userdata, flags, rc=0):
#         print(f"disconnected result code {str(rc)}")

#     def on_log(client, userdata, level, buf):
#         print(f"log: {buf}")

#     # client 생성
#     client_id = "mqtt_client_111"
#     client = mqtt.Client(client_id)

#     # 콜백 함수 설정
#     client.on_connect = on_connect
#     client.on_disconnect = on_disconnect
#     client.on_log = on_log

#     # broker 연결
#     client.connect(host='106.245.229.11', port=1883)
#     return client


# def subscribe(client: mqtt):
#     def on_message(client, userdata, msg):
#         print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
#         return msg.payload.decode()

#     client.subscribe('/store/lock/result') #1
#     client.on_message = on_message



#     print('>>>>>>!! ', on_message)

#     return on_message
