"""获取单个股票基本信息"""
from typing import Dict, List
import json
from pydantic import BaseModel
from fastapi import APIRouter
from src.analysis.tushare_analysis import *
from src.analysis.akshare_analysis import *
from src.utils.store_util import *
from src.api.baostock_executor import BaoStockExecutor
from src.utils.logger_settings import api_logger

router = APIRouter()

class CodeItem(BaseModel):
    code:str = ''


@router.post("/stock_infos/get_base_infos")
async def get_stock_base_infos(params:CodeItem):
    """股票基本面信息"""
    api_logger.info(f"获取股票基本面信息，股票代码: {params.code}")
    res = {'code':200, 'msg':'查询成功', 'status':1, 'data':[]}
    try:
        code = params.code
        data = await BaoStockExecutor().get_base_data(code=code)
        api_logger.debug(f"成功获取股票基本面信息，股票代码: {code}，数据类别数量: {len(data)}")
        data = [{'name':k, 'data':v, 'columns': list(v[0].keys()) if len(v)>0 else []} for k,v in data.items()]
        res['data'] = data
        
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"获取股票基本面信息失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
        res['status'] = 0
    finally:
        return res