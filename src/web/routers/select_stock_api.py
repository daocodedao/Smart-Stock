from typing import Dict, List
import json
from pydantic import BaseModel
from src.utils.registy import ANALYSIS_REGISTRY_HISTORY, ANALYSIS_REGISTRY
from src.utils.constant import MARKET_TYPE
from fastapi import APIRouter
from src.engine.engine import Engine
from src.api.tushare_executor import TuShareExecutor
from src.analysis import *
from src.utils.common import get_all_stock_codes
from src.utils.store_util import *
from fastapi import Depends
from src.api.baostock_executor import BaoStockExecutor
from src.utils.registy import CLS_REGISTRY_ADDRESS
from src.utils.logger_settings import api_logger

router = APIRouter()

class SelectItem(BaseModel):
    """选股web传参
       {
           strategyParams:[{'code':'策略类名', 'params':[{'code':'参数1名','value':参数1值}]}],
           marketParams:[0,1,2,3]
       }
    """
    strategyParams: List = None
    marketParams: List = None

# api_logger 已经导入了

@router.post("/select_stocks/strategy_list")
async def get_strategy_list():
    api_logger.info("获取策略列表")
    # 使用加载后的模型进行预测
    res = {'code':200, 'msg':'请求成功', 'data':ANALYSIS_REGISTRY}
    return res

@router.post("/select_stocks/market_list")
async def get_marget_type():
    api_logger.info("获取市场类型列表")
    market_types = [{'code':k, 'name':v} for k,v in MARKET_TYPE.items()]
    res = {'code':200, 'msg':'请求成功', 'data':market_types}
    return res

@router.post("/select_stocks/get_selected_stock_data")
async def get_selected_stock_data(data:SelectItem, store_item=Depends(get_items)):
    api_logger.info(f"获取选股数据，策略数量: {len(data.strategyParams) if data.strategyParams else 0}")
    uuid_str = get_uuid()
    result = {'code':200, 'msg':'请求成功', 'data':[], 'tabNames':[], 'columns':[], 'uuidStr':uuid_str, 'totalNumbers':[], 'rawData':[]} #总条数
    try:
        strategy_params = data.strategyParams
        marget_params = data.marketParams
        #实例化分析器字符
        analysis_list = []
        for strategy in strategy_params:
            class_name = strategy['code']
            params = strategy.get('paramList', [])
            params_list = [f'market={marget_params}']
            for param in params:
                key = param['code']
                value = param['default']
                params_list.append(f'{key}={value}') 
            params_list = ','.join(params_list)
            analysis_list.append(eval(f"{class_name}({params_list})"))
        
        api_logger.debug(f"初始化分析器完成，分析器数量: {len(analysis_list)}")
        
        engine = Engine(api=TuShareExecutor())
        codes = get_all_stock_codes(market=marget_params)
        api_logger.debug(f"获取股票代码完成，代码数量: {len(codes)}")
        
        # codes = ['600640', '600641']
        params = {
                "ts_code": codes,
                "src": 'sina',
            }
        res = engine.execute(api_name='real_time_data', params=params, analyzer=analysis_list, codes=codes, return_list=False)
        api_logger.debug(f"执行选股引擎完成，结果分类数量: {len(res)}")
        
        res = {k:list_convert_science_number(v, keys=['流通市值', '总市值', '成交额']) for k,v in res.items()}
        store_item[uuid_str] =res  #存储到缓存用于分页
        result['data'] = {k:[] for k in res.keys()} #分页 此次请求只显示空列表
        result['tabNames'] = return_tab_name(res)
        result['rawData'] = res
        result['columns'] = return_columns(res)
        totalNumbers = [{'name':k, 'numbers':len(v)} for k,v in res.items()]
        result['totalNumbers'] = totalNumbers
        
        api_logger.info(f"选股完成，UUID: {uuid_str}, 结果分类数量: {len(res)}")
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"选股失败: {error_msg}")
        result['code'] = 500
        result['msg'] = error_msg
    finally:
        return result

class IndexItem(BaseModel):
    tabName:str
    uuidStr:str
    currentPage:int #当前页
    pageSize:int #每页数量
    
class UuidItem(BaseModel):
    uuidStr:str



@router.post("/select_stocks/get_selected_stock_data_by_index")
async def get_selected_stock_data_by_index(params:IndexItem, store_item=Depends(get_items)):
    api_logger.info(f"分页获取选股数据，UUID: {params.uuidStr}, 标签: {params.tabName}, 页码: {params.currentPage}, 每页数量: {params.pageSize}")
    res = {'code':200, 'msg':'请求成功', 'data':[]}
    try:
        res_data = get_by_index(uuid=params.uuidStr,
                                tab_name=params.tabName,
                                start=params.currentPage*params.pageSize,
                                length=params.pageSize,
                                items=store_item)
        
        api_logger.debug(f"分页获取选股数据成功，数据条数: {len(res_data)}")
        res['data'] = res_data
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"分页获取选股数据失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res

@router.post("/select_stocks/delete_cache")
async def del_selected_stock_cache(params:UuidItem):
    """删除缓存的cache"""
    api_logger.info(f"删除选股缓存，UUID: {params.uuidStr}")
    res = {'code':200, 'msg':'删除成功'}
    try:
        flag = delete_cache(params.uuidStr)
        result_msg = '删除失败' if not flag else '删除成功'
        api_logger.info(f"删除选股缓存结果: {result_msg}")
        res['msg'] = result_msg
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"删除选股缓存失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res
    
def return_tab_name(data):
    """返回tab name"""
    tab_names = []
    for k in data.keys():
        tab_names.append(k)
    return tab_names

def return_columns(data):
    columns = []
    try:
        for v in data.values():
            if len(v)>0:
                col = list(v[0].keys())
            else:
                col = []
            columns.append(col)
    except Exception as e:
        api_logger.error(f"获取列信息失败: {e}")
    finally:
        return columns



@router.post("/select_stocks/strategy_list_hisory")
async def get_strategy_list_history():
    api_logger.info("获取历史策略列表")
    # 使用加载后的模型进行预测
    res = {'code':200, 'msg':'请求成功', 'data':ANALYSIS_REGISTRY_HISTORY}
    return res

@router.post("/select_stocks/get_selected_stock_data_by_history")
async def get_selected_stock_data_by_history(data:SelectItem, store_item=Depends(get_items)):
    """根据历史数据选股"""
    api_logger.info(f"根据历史数据选股，策略数量: {len(data.strategyParams) if data.strategyParams else 0}")
    uuid_str = get_uuid()
    result = {'code':200, 'msg':'请求成功', 'data':[], 'tabNames':[], 'columns':[], 'uuidStr':uuid_str, 'totalNumbers':[], 'rawData':{}} #总条数
    try:
        strategy_params = data.strategyParams
        marget_params = data.marketParams
        #实例化分析器字符
        analysis_list = []
        for strategy in strategy_params:
            strategy_name = strategy['name']
            class_name = strategy['code']
            params = strategy.get('params', {})
            analysis_list.append({'name':strategy_name, 'instance':CLS_REGISTRY_ADDRESS[class_name](market=marget_params,params=params)})
        
        api_logger.debug(f"初始化历史分析器完成，分析器数量: {len(analysis_list)}")
        
        res = {}
        for instance in analysis_list:
            name = instance['name']
            cls_func = instance['instance']
            api_logger.debug(f"执行历史分析器: {name}")
            r = await cls_func.analysis()
            if isinstance(r, list):
                res[name] = r
            elif isinstance(r, dict):
                res.update(r)
        
        api_logger.debug(f"执行历史选股完成，结果分类数量: {len(res)}")
        
        store_item[uuid_str] =res  #存储到缓存用于分页
        result['data'] = {k:[] for k in res.keys()} #分页 此次请求只显示空列表
        result['rawData'] = res
        result['tabNames'] = return_tab_name(res)
        result['columns'] = return_columns(res)
        totalNumbers = [{'name':k, 'numbers':len(v)} for k,v in res.items()]
        result['totalNumbers'] = totalNumbers
        
        api_logger.info(f"历史选股完成，UUID: {uuid_str}, 结果分类数量: {len(res)}")
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"历史选股失败: {error_msg}")
        result['code'] = 500
        result['msg'] = error_msg
    finally:
        return result