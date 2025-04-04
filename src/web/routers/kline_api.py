from fastapi import APIRouter
from pydantic import BaseModel
from src.utils.common import *
from src.utils.stock_utils import *
import akshare as ak
from src.api.baostock_executor import BaoStockExecutor
from src.utils.logger_settings import api_logger

router = APIRouter()

class SelectDayItem(BaseModel):
    """获取单个股票近n年日k线数据
       {
           strategyParams:[{'code':'策略类名', 'params':[{'code':'参数1名','value':参数1值}]}],
           marketParams:[0,1,2,3]
       }
    """
    code: str = 'sh000001' #股票代码
    nYear: float = 2 #近多少年数据
    support: bool = False #可视化支撑压力线
    startDate:str = None
    endDate:str = None
    

    
@router.post('/kline/day')
async def find_day_k_line_data(param:SelectDayItem):
    """获取日线数据"""
    api_logger.info(f"获取日K线数据，股票代码: {param.code}, 年数: {param.nYear}")
    res = {'code':200, 'rawData':[], 'msg':'请求成功', 'supportData':{}}
    try:
        code = param.code
        n_fold = param.nYear
        try:
            df = get_day_k_data(code=code, n_folds=n_fold, start_date=param.startDate, end_date=param.endDate, return_list=True, api_type='abu')
            api_logger.debug(f"成功获取日K线数据，股票代码: {code}, 数据条数: {len(df)}")
            df_res = dftodict(df)
            res['rawData'] = df_res
        except ImportError as ie:
            # 处理 Iterable 导入错误
            api_logger.warning(f"导入错误: {str(ie)}，尝试使用替代方法")
            # 这里可以添加替代方案，例如使用其他API获取数据
            raise Exception(f"获取K线数据时遇到导入错误: {str(ie)}，请检查依赖库版本")
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"获取日K线数据失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res



class RealTimeItem(BaseModel):
    """实时分时数据
       {
           strategyParams:[{'code':'策略类名', 'params':[{'code':'参数1名','value':参数1值}]}],
           marketParams:[0,1,2,3]
       }
    """
    code: str = 'sh000001' #股票代码

@router.post('/kline/fenshi')
async def fenshi_k(params:RealTimeItem):
    api_logger.info(f"获取分时数据，股票代码: {params.code}")
    res ={'code':200, 'msg':'请求成功', 'data':[], 'date':[], 'meanData':[]}
    try:
        code = params.code
        hourData = []
        code = code_to_abu_code(code)
        df = ak.stock_zh_a_tick_tx_js(symbol=code)
        api_logger.debug(f"成功获取分时数据，股票代码: {code}, 数据条数: {len(df)}")
        date = df['成交时间'].to_list()
        df['均线'] = round(df['成交金额'].cumsum()/df['成交量'].cumsum()/100,2)
        for i, item in df.iterrows():
            item = item.to_list()
            hourData.append(item)
        res['hourData'] = hourData
        data = dftodict(df)
        res['data'] = data
        res['date'] = date
        res['meanData'] = df['均线'].to_list()
        
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"获取分时数据失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res

class KLineItem(SelectDayItem):
    frequency:str = 'd'

@router.post('/kline/kline_by_freq')
def get_k_line_by_frequency(param:KLineItem):
    """通过频率获取k线数据"""
    api_logger.info(f"获取K线数据，股票代码: {param.code}, 频率: {param.frequency}")
    res = {'code':200, 'rawData':[], 'msg':'请求成功'}
    try:
        code = param.code
        df = BaoStockExecutor().get_history_time_data(code=code, start_date=param.startDate, end_date=param.endDate, frequency=param.frequency)
        api_logger.debug(f"成功获取K线数据，股票代码: {code}, 频率: {param.frequency}, 数据条数: {len(df)}")
        res['rawData'] = df
    except Exception as e:
        error_msg = str(e)
        api_logger.error(f"获取K线数据失败: {error_msg}")
        res['code'] = 500
        res['msg'] = error_msg
    finally:
        return res
    
    

    