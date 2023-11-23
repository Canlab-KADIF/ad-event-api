# -*- coding: utf-8 -*-
from flask import Flask, send_from_directory
from flask_restx import Api
from flask_cors import CORS

######################################################################################################################
# api - src > guest
######################################################################################################################
from src.guest.login import Login

######################################################################################################################
# api - src > user
######################################################################################################################
from src.user.logout import Logout

######################################################################################################################
#  router - src > gn
######################################################################################################################
from src.gn.index import GnIndex
from src.gn.cmsMenuList import GnCmsMenuList
from src.gn.checkDuplicate import GnCheckDuplicate

############################################################
# /gn/sy
############################################################
from src.gn.sy.common import SyCommon
from src.gn.sy.commonMove import SyCommonMove
from src.gn.sy.userList import SyUserList
from src.gn.sy.user import SyUser
from src.gn.sy.userResetPassword import SyUserResetPassword
from src.gn.sy.menu import SyMenu
from src.gn.sy.menuMove import SyMenuMove
############################################################
# /gn/st
############################################################


############################################################
# /gn/pj
############################################################
from src.gn.pj.damageList import PjDamageList
from src.gn.pj.damage import PjDamage
from src.gn.pj.roadMap import PjRoadMap
# from src.gn.pj.category import PjCategory
# from src.gn.pj.keyword import PjKeyword
# from src.gn.pj.storeList import PjStoreList
# from src.gn.pj.store import PjStore
# from src.gn.pj.contentsList import PjContentsList
# from src.gn.pj.contents import PjContents
############################################################
# /gn/sa
############################################################

############################################################
# modal
############################################################
from src.gn.mdCategory import MdCategoryList
from src.gn.mdKeyword import MdKeywordList

pathole = Flask(__name__)

api = Api(
	pathole,
	version='0.1',
	title="도로 표면 정보 시스템",
	description="도로 표면 정보 시스템 API Server!",
	terms_url="/",
)

# cors 처리
# CORS(pathole, resources={r'*': {'origins': 'http://192.168.0.22:8082'}})
CORS(pathole)

# ( 'none', 'list'또는 'full')
pathole.config.SWAGGER_UI_DOC_EXPANSION = 'list'
pathole.config.SWAGGER_UI_OPERATION_ID = True
# pathole.config.SWAGGER_UI_REQUEST_DURATION = True



######################################################################################################################
#  router - src > guest
######################################################################################################################
api.add_namespace(Login, '/login')


######################################################################################################################
#  router - src > user
######################################################################################################################
api.add_namespace(Logout, '/logout')


######################################################################################################################
#  router - src > gn
######################################################################################################################
api.add_namespace(GnIndex, '/gn/index')
api.add_namespace(GnCmsMenuList, '/gn/menuList')
api.add_namespace(GnCheckDuplicate, '/gn/checkDuplicate')
############################################################
# /gn/sy
############################################################

# api.add_namespace(SyConfig, '/gn/sy/config')
api.add_namespace(SyCommon, '/gn/sy/common')
api.add_namespace(SyCommonMove, '/gn/sy/commonMove')
api.add_namespace(SyUserList, '/gn/sy/userList')
api.add_namespace(SyUser, '/gn/sy/user')

api.add_namespace(SyUserResetPassword, '/gn/sy/userResetPassword')

api.add_namespace(SyMenu, '/gn/sy/menu')
api.add_namespace(SyMenuMove, '/gn/sy/menuMove')

# api.add_namespace(SyCode, '/gn/sy/code')
# api.add_namespace(SyCodeMove, '/gn/sy/codeMove')


# api.add_namespace(SyHoliday, '/gn/sy/holiday')

############################################################
# /gn/st
############################################################


############################################################
# /gn/pj
############################################################
api.add_namespace(PjDamageList, '/gn/pj/damageList')
api.add_namespace(PjDamage, '/gn/pj/damage')
api.add_namespace(PjRoadMap, '/gn/pj/roadMap')
############################################################
# /gn/sa
############################################################

############################################################
# modal
############################################################
api.add_namespace(MdCategoryList, '/gn/mdCategoryList')
api.add_namespace(MdKeywordList, '/gn/mdKeywordList')

# run the pathole.
if __name__ == "__main__":
	pathole.run(debug=True, host='0.0.0.0', port=5001)

