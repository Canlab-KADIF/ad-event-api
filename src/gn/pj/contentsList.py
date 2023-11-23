# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
import datetime
from src.common.function import *

PjContentsList = Namespace('PjContentsList')

PjContentsListGet = PjContentsList.schema_model('PjContentsListGet', {

})

@PjContentsList.route('', methods=['GET'])
class PjContentsListApi(Resource):
    ####################################################################################################################
    # METHOD : GET
    # write  : 23.06.30
    # writer : chside
    ####################################################################################################################
    swagger = PjContentsList.parser()
    swagger.add_argument('Authorization', required=True, location='headers', help='로그인토큰')
    swagger.add_argument('searchRole', required=False, type=str, location='body', help='권한')
    swagger.add_argument('searchText', required=False, type=str, location='body', help='검색어')
    swagger.add_argument('page', required=False, type=int, location='body', help='페이지 번호 default : 1 ')
    swagger.add_argument('pageSize', required=False, type=int, location='body', help='페이지당 데이터수 default : 20')
    @PjContentsList.expect(swagger)

    @PjContentsList.doc(model=PjContentsListGet)

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
                # print(payload)
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
                c.seq,
                c.title,
                c.platform,
                (SELECT code_name FROM sy_common WHERE code_id = c.platform) AS platformNm,
                c.enter_dt,
                u.user_name,
                c.used
                """

                # table
                sql_table = """
                pj_contents c
                LEFT JOIN sy_user u ON u.seq = c.user_seq
                """

                # where
                sql_where = """
                c.delete_id IS NULL
                AND c.user_seq = %s
                """ % payload['userNo']

                # if searchRole is not None:
                # 	if searchRole == '0':
                # 		sql_where = sql_where + ""
                # 	else:
                # 		sql_where = sql_where + "AND u.role = '%s' " % searchRole

                # if searchText is not None:
                # 	sql_where = sql_where + "AND (store_name LIKE '%%%s%%' " % (searchText, searchText)

                # order by
                sql_order = "c.seq DESC "

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
                    item['contentsNo'] = row['seq']
                    item['title'] = row['title']
                    item['platform'] = row['platform']
                    item['platformNm'] = row['platformNm']
                    item['categoryList'] = get_category_list(row['seq'], svt)
                    item['keywordList'] = get_keyword_list(row['seq'], svt)
                    item['userName'] = row['user_name']
                    if row['enter_dt'] is not None:
                        item['enterDt'] = row['enter_dt'].strftime("%Y-%m-%d")
                    else:
                        item['enterDt'] = ''
                    item['used'] = row['used']
                    if row['used'] == '1':
                        item['usedNm'] = '사 용'
                    else:
                        item['usedNm'] = '중 지'
                    item['imageFile'] = get_contents_file(row['seq'], 'images', svt)
                    item['fileList'] = get_contents_file_list(row['seq'], svt)
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

