from typing import Any, Optional
import httpx
from mcp.server.fastmcp import FastMCP
import os

# Initialize FastMCP server
mcp = FastMCP("xueqiu")

# Constants
XUEQIU_API_BASE = "https://xueqiu.com"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"

# API Endpoints
FINANCE_CASH_FLOW_URL = "https://stock.xueqiu.com/v5/stock/finance/cn/cash_flow.json?symbol="
FINANCE_INDICATOR_URL = "https://stock.xueqiu.com/v5/stock/finance/cn/indicator.json?symbol="
FINANCE_BALANCE_URL = "https://stock.xueqiu.com/v5/stock/finance/cn/balance.json?symbol="
FINANCE_INCOME_URL = "https://stock.xueqiu.com/v5/stock/finance/cn/income.json?symbol="
FINANCE_BUSINESS_URL = "https://stock.xueqiu.com/v5/stock/finance/cn/business.json?symbol="

CAPITAL_MARGIN_URL = "https://stock.xueqiu.com/v5/stock/capital/margin.json?symbol="
CAPITAL_BLOCKTRANS_URL = "https://stock.xueqiu.com/v5/stock/capital/blocktrans.json?symbol="
CAPITAL_ASSORT_URL = "https://stock.xueqiu.com/v5/stock/capital/assort.json?symbol="
CAPITAL_HISTORY_URL = "https://stock.xueqiu.com/v5/stock/capital/history.json?symbol="
CAPITAL_FLOW_URL = "https://stock.xueqiu.com/v5/stock/capital/flow.json?symbol="

async def make_xueqiu_request(url: str) -> dict[str, Any] | None:
         
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": "https://xueqiu.com",
        "Host": "stock.xueqiu.com",
        "Accept": "application/json",
        "Cookie": "xq_a_token=71f859f915f8b662973e99748f9a6f58a57fec63; xq_r_token=c9f620b0b6a96a10159d3a2d0fcb2aafb451a359"
    }
    async with httpx.AsyncClient() as client:
        for attempt in range(3):
            try:
                print(f"尝试第{attempt + 1}次请求: {url}")
                response = await client.get(url, headers=headers, timeout=30.0)
                print(f"请求成功，状态码: {response.status_code}")
                response.raise_for_status()
                json_data = response.json()
                print(f"响应数据: {json_data}")
                return json_data
            except Exception as e:
                print(f"请求失败: {e}")
                if attempt == 2:
                    print(f"所有重试均失败: {url}")
                    return None
                continue

@mcp.tool(
    name="get_realtime_quote",
    description="获取股票实时行情数据"
)
async def get_realtime_quote(symbol: str) -> str:
    """获取股票实时行情数据
    
    Args:
        symbol (str): 股票代码，如: SH000001
    """
    url = f"https://stock.xueqiu.com/v5/stock/realtime/quotec.json?symbol={symbol}"
    data = await make_xueqiu_request(url)
    
    if not data or not isinstance(data, dict) or not data.get("data"):
        return "获取行情数据失败"
    quote = data["data"][0]
    return f"""
📊 {quote.get('symbol', '未知')}
当前价: {quote.get('current', 'N/A')}
涨跌幅: {quote.get('percent', 'N/A')}%
涨跌额: {quote.get('chg', 'N/A')}
最高价: {quote.get('high', 'N/A')}
最低价: {quote.get('low', 'N/A')}
开盘价: {quote.get('open', 'N/A')}
昨收价: {quote.get('last_close', 'N/A')}
成交量: {quote.get('volume', 'N/A')}手
成交额: {quote.get('amount', 'N/A')}元
市值: {quote.get('market_capital', 'N/A')}元
换手率: {quote.get('turnover_rate', 'N/A')}%
振幅: {quote.get('amplitude', 'N/A')}%
"""

@mcp.tool(
    name="get_cash_flow",
    description="获取股票现金流数据"
)
async def get_cash_flow(symbol: str) -> str:
    """获取股票现金流数据
    
    Args:
        symbol (str): 股票代码，如: SH000001
    """
    url = f"{FINANCE_CASH_FLOW_URL}{symbol}"
    data = await make_xueqiu_request(url)
    
    if not data or not isinstance(data, dict) or not data.get("data"):
        return "获取现金流数据失败"
    
    result = [f"📊 {symbol} 现金流数据"]
    result.append("=" * 40)
    
    for item in data["data"]["list"]:
        result.append(f"\n报告期: {item['report_name']}")
        result.append("-" * 30)
        result.append(f"经营活动现金流净额: {format(item['ncf_from_oa'][0], ',')}元 (同比增长: {item['ncf_from_oa'][1]*100:.2f}%)")
        result.append(f"投资活动现金流净额: {format(item['ncf_from_ia'][0], ',')}元 (同比增长: {item['ncf_from_ia'][1]*100:.2f}%)")
        result.append(f"筹资活动现金流净额: {format(item['ncf_from_fa'][0], ',')}元 (同比增长: {item['ncf_from_fa'][1]*100:.2f}%)")
        result.append("=" * 40)
    
    return "\n".join(result)

@mcp.tool(
    name="get_financial_indicator",
    description="获取股票财务指标数据"
)
async def get_financial_indicator(symbol: str) -> str:
    """获取股票财务指标数据
    
    Args:
        symbol (str): 股票代码，如: SH000001
    """
    url = f"{FINANCE_INDICATOR_URL}{symbol}"
    data = await make_xueqiu_request(url)
    
    if not data or not isinstance(data, dict) or not data.get("data"):
        return "获取财务指标数据失败"
    
    result = [f"📊 {symbol} 财务指标数据"]
    result.append("=" * 40)

    # Helper functions for safe formatting
    def safe_format_percent(value):
        try:
            # Handle None or empty string explicitly
            if value is None or value == '':
                return 'N/A'
            # Attempt conversion only if it looks like a number
            if isinstance(value, (int, float)):
                 return f"{float(value)*100:.2f}%"
            elif isinstance(value, str):
                 # Handle 'N/A' explicitly
                 if value == 'N/A':
                     return 'N/A'
                 # Handle potential strings that represent numbers
                 cleaned_value = value.replace('%', '') # Remove percent sign if present
                 # Check if cleaned value is numeric before converting
                 is_numeric = False
                 try:
                     float(cleaned_value)
                     is_numeric = True
                 except ValueError:
                     pass
                 
                 if is_numeric:
                     return f"{float(cleaned_value)*100:.2f}%"
                 else:
                     return str(value) # Return as is if not numeric
            else:
                 return str(value) # Return as is if not convertible
        except (ValueError, TypeError):
            return str(value) # Fallback for any conversion error
    
    for item in data["data"]["list"]:
        result.append(f"\n报告期: {item['report_name']}")
        result.append("-" * 30)
        # 安全处理可能是字符串的数值，默认为'N/A'
        basic_eps = item.get('basic_eps', ['N/A', 'N/A'])
        avg_roe = item.get('avg_roe', ['N/A', 'N/A'])
        gross_selling_rate = item.get('gross_selling_rate', ['N/A', 'N/A'])
        
        # 格式化输出，使用辅助函数确保安全
        result.append(f"每股收益(EPS): {basic_eps[0]} (同比增长: {safe_format_percent(basic_eps[1])})")
        result.append(f"净资产收益率(ROE): {safe_format_percent(avg_roe[0])} (同比增长: {safe_format_percent(avg_roe[1])})")
        result.append(f"毛利率: {safe_format_percent(gross_selling_rate[0])} (同比增长: {safe_format_percent(gross_selling_rate[1])})")
        result.append("=" * 40)
    
    return "\n".join(result)

if __name__ == "__main__":
    # 测试代码块
    #import asyncio
    #async def test():
    #    result = await get_cash_flow("SH601919")
    #    print(result)
    
    # 运行测试
    #asyncio.run(test())
    
    # 保持原有功能
    mcp.run(transport='stdio')