from pydantic import BaseModel
from src.utils.common import *
from fastapi import APIRouter
from src.database.mysql_user_util import *
from src.utils.constant import *
from src.utils.logger_settings import api_logger

router = APIRouter()

class UserItem(BaseModel):
    userID: str #用户id
    email: str = ''# email
    userName: str = '' #用户名
    password: str #密码

class LoginItem(BaseModel):
    userID: str
    password: str

class ResetItem(BaseModel):
    userID: str
    password: str
    newPassword: str


@router.post('/user/registry')
async def registry(params:UserItem):
    api_logger.info(f"用户注册请求，用户ID: {params.userID}, 用户名: {params.userName}")
    result = {'code':200, 'msg':'', 'status':1}
    try:
        util = MysqlUserUtil(host=HOST,
                            user=USER,
                            password=PASSWORD,
                            database=DATABASE,
                            db_port=DB_PORT)
        res, msg = util.registry(user_id=params.userID,
                    user_name=params.userName,
                    password=params.password,
                    email=params.email)
        result['status'] = int(res)
        result['msg'] = msg
        api_logger.info(f"用户注册结果: {msg}, 状态: {res}")
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"用户注册失败: {error_msg}")
        result['code'] = 500
        result['msg'] = error_msg
    finally:
        return result

@router.post('/user/login')
async def login(params:LoginItem):
    api_logger.info(f"用户登录请求，用户ID: {params.userID}")
    result = {'code':200, 'msg':'', 'status':1, 'userToken':''}
    try:
        get_logger().info(f"{params.userID}登录系统!")
        util = MysqlUserUtil(host=HOST,
                            user=USER,
                            password=PASSWORD,
                            database=DATABASE,
                            db_port=DB_PORT)
        res, msg = util.login(user_id=params.userID,
                    password=params.password)
        result['status'] = int(res)
        result['msg'] = msg
        result['userToken'] = get_uuid()
        api_logger.info(f"用户登录结果: {msg}, 状态: {res}")
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"用户登录失败: {error_msg}")
        result['code'] = 500
        result['msg'] = error_msg
    finally:
        return result

@router.post('/user/reset_password')
async def reset_password(params:ResetItem):
    api_logger.info(f"用户重置密码请求，用户ID: {params.userID}")
    result = {'code':200, 'msg':'', 'status':1, 'userToken':''}
    try:
        util = MysqlUserUtil(host=HOST,
                            user=USER,
                            password=PASSWORD,
                            database=DATABASE,
                            db_port=DB_PORT)
        res, msg = util.reset_password(user_id=params.userID,
                    password=params.password,
                    new_password=params.newPassword)
        result['status'] = int(res)
        result['msg'] = msg
        result['userToken'] = get_uuid()
        api_logger.info(f"用户重置密码结果: {msg}, 状态: {res}")
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"用户重置密码失败: {error_msg}")
        result['code'] = 500
        result['msg'] = error_msg
    finally:
        return result