from pydantic import BaseModel
from src.utils.common import *
from fastapi import APIRouter
from src.database.mysql_order_util import *
from src.utils.constant import *
from fastapi import Depends
from src.utils.store_util import *
from src.api.tushare_executor import TuShareExecutor
from src.utils.logger_settings import api_logger

router = APIRouter()

class OrderItem(BaseModel):
    userID: str #用户id
    stockName: str #股票名
    tradeDate: str #交易日期
    volume: int #成交量
    price: float #成交价
    stockStatus: int #买/卖
    
class UpdateItem(OrderItem):
    id:int #自动生成的id 更新时使用
    
@router.post('/order/add_order')
async def add_order(params:OrderItem):
    """新增交割单"""
    api_logger.info(f"添加交割单，用户ID: {params.userID}, 股票名: {params.stockName}")
    res = {'code':200, 'msg':'请求成功', 'status': 1}
    try:
        mysql_util = MysqlOrderUtil(host=HOST,
                            user=USER,
                            password=PASSWORD,)
        r, msg = mysql_util.add_order(user_id=params.userID,
                             stock_name=params.stockName,
                             trade_date=params.tradeDate,
                             volume=params.volume,
                             price=params.price,
                             stockStatus=params.stockStatus)
        res['status'] = int(r)
        res['msg'] = msg
        api_logger.info(f"添加交割单结果: {msg}, 状态: {r}")
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"添加交割单失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res

@router.post('/order/update_order')
async def update_order(params:UpdateItem):
    """新增交割单"""
    api_logger.info(f"更新交割单，用户ID: {params.userID}, 股票名: {params.stockName}, ID: {params.id}")
    res = {'code':200, 'msg':'请求成功', 'status': 1}
    try:
        mysql_util = MysqlOrderUtil(host=HOST,
                            user=USER,
                            password=PASSWORD,)
        r, msg = mysql_util.update_order(
                             user_id=params.userID,
                             stock_name=params.stockName,
                             trade_date=params.tradeDate,
                             volume=params.volume,
                             price=params.price,
                             stock_status=params.stockStatus,
                             id=params.id)
        res['status'] = int(r)
        res['msg'] = msg
        api_logger.info(f"更新交割单结果: {msg}, 状态: {r}")
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"更新交割单失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res

class DeleteItem(BaseModel):
    userID: str
    id: int

@router.post('/order/delete_order')
async def delete_order(params:DeleteItem):
    """新增交割单"""
    api_logger.info(f"删除交割单，用户ID: {params.userID}, ID: {params.id}")
    res = {'code':200, 'msg':'请求成功', 'status': 1}
    try:
        mysql_util = MysqlOrderUtil(host=HOST,
                            user=USER,
                            password=PASSWORD,)
        r, msg = mysql_util.delete_order(id=params.id, user_id=params.userID)
        res['status'] = int(r)
        res['msg'] = msg
        api_logger.info(f"删除交割单结果: {msg}, 状态: {r}")
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"删除交割单失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res

class SelectItem(BaseModel):
    userID:str 
    stockName:str=None
    analysis:bool=False #分析收益率
    summary:bool=False #是否汇总
    
class SelectItemByIndex(SelectItem):
    """分页查询"""
    uuidStr:str
    currentPage:int #当前页
    pageSize:int #每页数量
    

@router.post('/order/select_order')
async def select_order(params:SelectItem):
    """查询"""
    api_logger.info(f"查询交割单，用户ID: {params.userID}, 股票名: {params.stockName}, 分析: {params.analysis}, 汇总: {params.summary}")
    res = {'code':200, 'msg':'请求成功', 'data':[], 'columns':[], 'totalNumbers':0, 'uuidStr':''}
    try:
        mysql_util = MysqlOrderUtil(host=HOST,
                            user=USER,
                            password=PASSWORD,)
        uuid_str = get_uuid()
        res['uuidStr'] = uuid_str
        if not params.summary:
            data, msg = mysql_util.select_order(stock_name=params.stockName, user_id=params.userID)
        else:
            data, msg = mysql_util.select_order_and_sum(user_id=params.userID, stock_name=params.stockName)
        
        api_logger.debug(f"查询到交割单数据: {len(data)}条")
        
        if params.analysis:
            codes = [x['代码'] for x in data]
            params = {
                "ts_code": codes,
                "src": 'sina',
            }
            res_list = TuShareExecutor().get_real_time_data(params=params, name_convert=False, return_list=True) #分析涨跌额
            if len(res_list)>0:
                for x in data:
                    code = x['代码']
                    for y in res_list:
                        if code in y['ts_code']:
                            price = y['price']
                            if x['状态'] !='empty':
                                x['收益'] = str(round(100*(float(price)-float(x['价格']))/float(x['价格']),3)) +'%'
                            else:
                                x['收益'] = -x['成交额']
        store_order_data(uuid=uuid_str, infos=data) #缓存
        res['totalNumbers'] = len(data)
        if len(data)>100:
            res['data'] = [] #分页
        else:
            res['data'] = data
        if len(data)>0:
            res['columns'] = list(data[0].keys())
        res['msg'] = msg
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"查询交割单失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res

@router.post('/order/select_order_by_index')
async def select_order_by_index(params:SelectItemByIndex, items=Depends(get_order_cache)):
    """查询"""
    api_logger.info(f"分页查询交割单，用户ID: {params.userID}, 页码: {params.currentPage}, 每页数量: {params.pageSize}")
    res = {'code':200, 'msg':'请求成功', 'data':[], 'columns':[]}
    try:
        data = get_order_by_index(uuid=params.uuidStr,
                                    start=params.currentPage,
                                    length=params.pageSize,
                                    items=items)
        api_logger.debug(f"分页查询到交割单数据: {len(data)}条")
        res['data'] = data
        if len(data)>0:
            res['columns'] = list(data[0].keys())
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"分页查询交割单失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res
