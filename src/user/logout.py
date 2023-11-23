# -*- coding: utf-8 -*-
import logging
import traceback
logging.basicConfig(level=logging.ERROR)

from flask import request
from flask_restx import Resource, Namespace, reqparse
from src.common.function import *

Logout = Namespace('Logout')

# 메소드별 모델 생성
LogoutPost = Logout.schema_model('LogoutPost', {
    "$schema": "http://json-schema.org/draft-04/schema#",
	"type": "object",
	"properties": {
		"timestamp": {
			"type": "string"
		}
	},
	"required": [
		"timestamp"
	]
})


@Logout.route('', methods=['POST'])

class LogoutApi(Resource):
    # swagger 파라미터
    # parser = Logout.parser()
    # parser.add_argument('Authorization', required=True)
    # parser.add_argument('deviceId', required=True, location='headers')

    # @Logout.expect(parser)

    # Example Value
    @Logout.doc(model=LogoutPost)

    def post(self):
        """
        로그아웃
        - 필수: Authorization
        - 일반:
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

        # DB 시작
        # cursor = mysql_cursor(mysql_conn(st))
        conn = mysql_conn(svt)
        cursor = mysql_cursor(conn)

        try:
            hasParam = True

            if hasParam:
                # device_id = parameter['deviceId']
                userNo = payload['userNo']

                # 회원정보를 가져와서 해당 리플래시 토큰이 사용되지 않도록 제거한다.
                # conn.begin()
                # try:
                #     sql = "UPDATE sy_user SET refreshToken = null WHERE seq = %s "
                #     cursor.execute(query=sql, args=userNo)

                # except Exception as e:
                #     conn.rollback()
                #     raise

                # else:
                #     conn.commit()

            else:
                statusCode = 404
                data['error'] = 'No Parameter'

        except Exception as e:
            logging.error(traceback.format_exc())
            data['error'] = 'exception error'
            statusCode = 505
            return data, statusCode

        finally:
            # DB 종료
            cursor.close()

        return json_null_to_empty(data), statusCode
