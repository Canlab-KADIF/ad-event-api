# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse

from werkzeug.datastructures import FileStorage
import datetime
from src.common.function import *

PjContents = Namespace('PjContents')

PjContentsGet = PjContents.schema_model('PjContentsGet', {
})
PjContentsPost = PjContents.schema_model('PjContentsPost', {
})
PjContentsPut = PjContents.schema_model('PjContentsPut', {
})
PjContentsDelete = PjContents.schema_model('PjContentsDelete', {
})

@PjContents.route('', methods=['GET','POST','PUT','DELETE'])

class PjContentsApi(Resource):
    ####################################################################################################################
    # METHOD : GET
    # write  : 23.03.31
    # writer : chside
    ####################################################################################################################
    # swagger 파라미터
    swagger = PjContents.parser()
    swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
    swagger.add_argument('contentsNo', type=int, required=True, location='body', help='pj_contents.seq')
    @PjContents.expect(swagger)

    @PjContents.doc(model=PjContentsGet)

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
        parser=reqparse.RequestParser()
        parser.add_argument('contentsNo', type=int, required=True, location='args')
        parameter = parser.parse_args()

        # DB 시작
        cursor = mysql_cursor(mysql_conn(svt))

        try:
            hasParam = True

            if 'contentsNo' not in parameter or not parameter['contentsNo']:
                hasParam = False

            if hasParam:
                contentsNo = parameter['contentsNo']

                sql = """
                SELECT
                    c.seq,
                    c.title,
                    c.platform,
                    (SELECT code_name FROM sy_common WHERE code_id = c.platform) AS platformNm,
                    c.memo,
                    c.enter_dt,
                    u.user_name,
                    c.used
                FROM pj_contents c
                    LEFT JOIN sy_user u ON u.seq = c.user_seq
                WHERE
                    c.delete_id IS NULL
                    AND c.seq = %s
                """
                cursor.execute(query=sql, args=contentsNo)
                row = cursor.fetchone()

                if row is not None:
                    data['contentsNo'] = row['seq']
                    data['title'] = row['title']
                    data['platform'] = row['platform']
                    data['platformNm'] = row['platformNm']
                    data['categoryList'] = get_category_list(contentsNo, svt)
                    data['keywordList'] = get_keyword_list(contentsNo, svt)
                    data['memo'] = row['memo']
                    data['fileList'] = get_contents_file_list(contentsNo, svt)
                    data['enterDt'] = row['enter_dt'].strftime("%Y-%m-%d")
                    data['userName'] = row['user_name']
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
    # METHOD : POST
    # write  : 23.03.31
    # writer : chside
    ####################################################################################################################
    # swagger 파라미터
    swagger = PjContents.parser()
    swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
    swagger.add_argument('title',         required=True,  type=str, location='body', help='컨텐츠명')
    swagger.add_argument('enterDt',       required=True,  type=str, location='body', help='등록일')
    swagger.add_argument('platform',      required=True,  type=str, location='body', help='플렛폼')
    swagger.add_argument('categoryList',  required=True,  type=str, location='body', help='선택한 카테고리')
    swagger.add_argument('keywordList',   required=False, type=str, location='body', help='선택한 키워드')
    swagger.add_argument('memo',          required=True,  type=str, location='body', help='컨텐츠 설명')
    swagger.add_argument('installFile',   required=False, type=FileStorage, location='files', help='설치파일')
    swagger.add_argument('eduFile',       required=False, type=FileStorage, location='files', help='교육파일')
    swagger.add_argument('imageFile',     required=False, type=FileStorage, location='files', help='이미지')
    @PjContents.expect(swagger)

    @PjContents.doc(model=PjContentsPost)

    def post(self):
        """
        회원정보 등록
        필수 : Authorization, title, enterDt, categoryList, memo, loginYn
        일반 : keywordList, installFile, eduFile, imageFile
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
        parser.add_argument('title',        required=True,  type=str)
        parser.add_argument('enterDt',      required=True,  type=str)
        parser.add_argument('platform',     required=True,  type=str)
        parser.add_argument('categoryList', required=True,  type=str)
        parser.add_argument('keywordList',  required=False, type=str)
        parser.add_argument('memo',         required=True,  type=str)
        parser.add_argument('installFile',  required=False, type=FileStorage)
        parser.add_argument('eduFile',      required=False, type=FileStorage)
        parser.add_argument('imageFile',    required=False, type=FileStorage)
        parameter = parser.parse_args()

        # DB 시작
        # cursor = mysql_cursor(mysql_conn(svt))
        conn = mysql_conn(svt)
        cursor = mysql_cursor(conn)

        try:
            hasParam = True

            if 'title' not in parameter or not parameter['title']:
                hasParam = False

            if 'enterDt' not in parameter or not parameter['enterDt']:
                hasParam = False

            if 'platform' not in parameter or not parameter['platform']:
                hasParam = False

            if 'categoryList' not in parameter or not parameter['categoryList']:
                hasParam = False

            if 'memo' not in parameter or not parameter['memo']:
                hasParam = False

            if hasParam :
                title = parameter['title']
                enterDt = parameter['enterDt']
                platform = parameter['platform']
                categoryList = json.loads(parameter['categoryList'])
                memo = parameter['memo']

                keywordList = None
                if 'keywordList' in parameter and parameter['keywordList'] != '':
                    keywordList = json.loads(parameter['keywordList'])

                installFile = None
                if 'installFile' in request.files:
                    installFile = request.files['installFile']

                eduFile = None
                if 'eduFile' in request.files:
                    eduFile = request.files['eduFile']

                imageFile = None
                if 'imageFile' in request.files:
                    imageFile = request.files['imageFile']

                # transation 시작
                conn.begin()
                try:
                    # 컨텐츠 등록
                    sql = """
                        INSERT INTO pj_contents(user_seq, title, platform, memo, enter_dt, insert_id, insert_ip)
                        VALUES(%s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query=sql, args=(payload['userNo'], title, platform, memo, enterDt, payload['userId'], userIp))
                    data['contentsNo'] = cursor.lastrowid

                    # 카테고리 등록
                    if categoryList is not None:
                        for crow in categoryList:
                            sql = """
                            INSERT INTO pj_contents_category (contents_seq, user_seq, category_seq, insert_id, insert_ip)
                            VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(query=sql, args=(data['contentsNo'], payload['userNo'], crow['categoryNo'], payload['userId'], userIp))

                    # 키워드 등록
                    if keywordList is not None:
                        for krow in keywordList:
                            sql = """
                            INSERT INTO pj_contents_keyword (contents_seq, user_seq, keyword_seq, insert_id, insert_ip)
                            VALUES (%s, %s, %s, %s, %s)
                            """
                            cursor.execute(query=sql, args=(data['contentsNo'], payload['userNo'], krow['keywordNo'], payload['userId'], userIp))

                    # 첨부파일 - 설치파일
                    if installFile is not None:
                        tblId = 'contents'
                        tblType = 'install'
                        thumbYn = 'N'
                        res = fileUpload(installFile, tblId, tblType, data['contentsNo'], thumbYn, payload, userIp, svt)

                    # 첨부파일 - 교육파일
                    if eduFile is not None:
                        tblId = 'contents'
                        tblType = 'edu'
                        thumbYn = 'N'
                        res2 = fileUpload(eduFile, tblId, tblType, data['contentsNo'], thumbYn, payload, userIp, svt)

                    # 첨부파일 - 이미지
                    if imageFile is not None:
                        tblId = 'contents'
                        tblType = 'images'
                        thumbYn = 'Y'
                        res2 = fileUpload(imageFile, tblId, tblType, data['contentsNo'], thumbYn, payload, userIp, svt)

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
    # write  : 23.03.31
    # writer : chside
    ####################################################################################################################
    # swagger 파라미터
    swagger = PjContents.parser()
    swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
    swagger.add_argument('categoryNo',    type=str, required=True, location='body')
    swagger.add_argument('title',         type=str, required=True, location='body')
    @PjContents.expect(swagger)

    @PjContents.doc(model=PjContentsPost)

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
    swagger = PjContents.parser()
    swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
    swagger.add_argument('contentsNo', type=int, required=False, location='body', help='pj_category.seq')
    @PjContents.expect(swagger)

    @PjContents.doc(model=PjContentsDelete)

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
        parser.add_argument('contentsNo', type=int, required=True, location='args')
        parameter = parser.parse_args()

        # DB 시작
        # cursor = mysql_cursor(mysql_conn(svt))
        conn = mysql_conn(svt)
        cursor = mysql_cursor(conn)

        try:
            hasParam = True

            if 'contentsNo' not in parameter or not parameter['contentsNo']:
                hasParam = False

            if hasParam :
                contentsNo = parameter['contentsNo']
                now = datetime.datetime.now().isoformat()
                # transation 시작
                conn.begin()

                try:
                    # 카테고리 삭제
                    sql = "DELETE FROM pj_contents_category WHERE contents_seq = %s AND user_seq = %s"
                    cursor.execute(query=sql, args=(contentsNo, payload['userNo']))

                    # 키워드 삭제
                    sql = "DELETE FROM pj_contents_keyword WHERE contents_seq = %s AND user_seq = %s"
                    cursor.execute(query=sql, args=(contentsNo, payload['userNo']))

                    # 컨텐츠 삭제
                    sql = "UPDATE pj_contents SET delete_id = %s, delete_dt = %s, delete_ip = %s WHERE seq = %s"
                    cursor.execute(query=sql, args=(payload['userId'], now, userIp, contentsNo))

                    # 파일 삭제



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
