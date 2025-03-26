from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from app.core.config import settings
from app.core.logging_config import logger
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.crawler import StockData
from app.models.analysis import StockAnalysis
import talib

class AnalysisService:
    def __init__(self):
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=0.95)  # 保留95%的方差

    def clean_financial_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """清理财务数据，处理异常值和缺失值"""
        try:
            # 处理缺失值
            data = data.fillna(method='ffill').fillna(method='bfill')
            
            # 处理异常值（使用IQR方法）
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            data = data[~((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))).any(axis=1)]
            
            return data
            
        except Exception as e:
            logger.error(f"财务数据清理失败: {str(e)}")
            return data

    def calculate_financial_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """计算关键财务指标"""
        try:
            metrics = {}
            
            # 收入增长率
            if 'revenue' in data and len(data['revenue']) > 1:
                revenue_growth = (data['revenue'][-1] - data['revenue'][-2]) / data['revenue'][-2]
                metrics['revenue_growth'] = revenue_growth
            
            # 毛利率
            if 'gross_profit' in data and 'revenue' in data:
                gross_margin = data['gross_profit'][-1] / data['revenue'][-1]
                metrics['gross_margin'] = gross_margin
            
            # 净利率
            if 'net_income' in data and 'revenue' in data:
                net_margin = data['net_income'][-1] / data['revenue'][-1]
                metrics['net_margin'] = net_margin
            
            # ROE
            if 'net_income' in data and 'equity' in data:
                roe = data['net_income'][-1] / data['equity'][-1]
                metrics['roe'] = roe
            
            # 资产负债率
            if 'total_liabilities' in data and 'total_assets' in data:
                debt_ratio = data['total_liabilities'][-1] / data['total_assets'][-1]
                metrics['debt_ratio'] = debt_ratio
            
            return metrics
            
        except Exception as e:
            logger.error(f"财务指标计算失败: {str(e)}")
            return {}

    def analyze_technical_indicators(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """计算技术指标"""
        try:
            results = {}
            
            # 计算移动平均线
            results['ma_5'] = price_data['close'].rolling(window=5).mean()
            results['ma_20'] = price_data['close'].rolling(window=20).mean()
            results['ma_60'] = price_data['close'].rolling(window=60).mean()
            
            # 计算RSI
            delta = price_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            results['rsi'] = 100 - (100 / (1 + rs))
            
            # 计算MACD
            exp1 = price_data['close'].ewm(span=12, adjust=False).mean()
            exp2 = price_data['close'].ewm(span=26, adjust=False).mean()
            results['macd'] = exp1 - exp2
            results['signal'] = results['macd'].ewm(span=9, adjust=False).mean()
            
            # 计算布林带
            results['bb_middle'] = price_data['close'].rolling(window=20).mean()
            results['bb_upper'] = results['bb_middle'] + 2 * price_data['close'].rolling(window=20).std()
            results['bb_lower'] = results['bb_middle'] - 2 * price_data['close'].rolling(window=20).std()
            
            return results
            
        except Exception as e:
            logger.error(f"技术指标计算失败: {str(e)}")
            return {}

    def detect_anomalies(self, data: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
        """检测异常值"""
        try:
            # 标准化数据
            scaled_data = self.scaler.fit_transform(data)
            
            # 使用PCA进行降维
            pca_data = self.pca.fit_transform(scaled_data)
            
            # 计算重构误差
            reconstructed_data = self.pca.inverse_transform(pca_data)
            reconstruction_error = np.mean(np.square(scaled_data - reconstructed_data), axis=1)
            
            # 标记异常值
            anomalies = reconstruction_error > threshold
            
            return data[anomalies]
            
        except Exception as e:
            logger.error(f"异常值检测失败: {str(e)}")
            return pd.DataFrame()

    def calculate_correlation(self, data1: pd.Series, data2: pd.Series) -> float:
        """计算相关性"""
        try:
            return data1.corr(data2)
        except Exception as e:
            logger.error(f"相关性计算失败: {str(e)}")
            return 0.0

    def calculate_volatility(self, price_data: pd.Series, window: int = 20) -> pd.Series:
        """计算波动率"""
        try:
            log_returns = np.log(price_data / price_data.shift(1))
            return log_returns.rolling(window=window).std() * np.sqrt(252)
        except Exception as e:
            logger.error(f"波动率计算失败: {str(e)}")
            return pd.Series()

    def analyze_stock_data(self, df: pd.DataFrame) -> Dict:
        """分析股票数据,计算技术指标"""
        try:
            # 确保数据按日期排序
            df = df.sort_index()
            
            # 计算移动平均线
            ma_5 = talib.SMA(df['close'], timeperiod=5)[-1]
            ma_10 = talib.SMA(df['close'], timeperiod=10)[-1]
            ma_20 = talib.SMA(df['close'], timeperiod=20)[-1]
            
            # 计算RSI
            rsi = talib.RSI(df['close'], timeperiod=14)[-1]
            
            # 计算MACD
            macd, macd_signal, macd_hist = talib.MACD(df['close'])
            macd = macd[-1]
            macd_signal = macd_signal[-1]
            macd_hist = macd_hist[-1]
            
            # 计算布林带
            upper, middle, lower = talib.BBANDS(df['close'])
            bollinger_upper = upper[-1]
            bollinger_middle = middle[-1]
            bollinger_lower = lower[-1]
            
            # 计算波动率
            volatility = df['close'].pct_change().std() * np.sqrt(252)
            
            # 计算ATR
            atr = talib.ATR(df['high'], df['low'], df['close'])[-1]
            
            # 判断趋势
            trend = self._determine_trend(df)
            trend_strength = self._calculate_trend_strength(df)
            
            # 计算支撑和阻力位
            support_levels, resistance_levels = self._calculate_support_resistance(df)
            
            # 计算技术评分
            technical_score = self._calculate_technical_score(
                df, ma_5, ma_10, ma_20, rsi, macd, macd_signal
            )
            
            # 确定风险水平
            risk_level = self._determine_risk_level(
                volatility, technical_score, trend_strength
            )
            
            # 生成交易建议
            trading_suggestion = self._generate_trading_suggestion(
                technical_score, risk_level, trend
            )
            
            return {
                'ma_5': ma_5,
                'ma_10': ma_10,
                'ma_20': ma_20,
                'rsi_14': rsi,
                'macd': macd,
                'macd_signal': macd_signal,
                'macd_hist': macd_hist,
                'bollinger_upper': bollinger_upper,
                'bollinger_middle': bollinger_middle,
                'bollinger_lower': bollinger_lower,
                'volatility': volatility,
                'atr': atr,
                'trend': trend,
                'trend_strength': trend_strength,
                'support_levels': support_levels,
                'resistance_levels': resistance_levels,
                'technical_score': technical_score,
                'risk_level': risk_level,
                'trading_suggestion': trading_suggestion
            }
            
        except Exception as e:
            logger.error(f"分析股票数据时发生错误: {str(e)}")
            return {}
            
    def _determine_trend(self, df: pd.DataFrame) -> str:
        """判断趋势方向"""
        try:
            # 使用20日移动平均线的斜率判断趋势
            ma_20 = talib.SMA(df['close'], timeperiod=20)
            slope = (ma_20[-1] - ma_20[-20]) / 20
            
            if slope > 0.01:
                return "上升"
            elif slope < -0.01:
                return "下降"
            else:
                return "横盘"
                
        except Exception as e:
            logger.error(f"判断趋势时发生错误: {str(e)}")
            return "未知"
            
    def _calculate_trend_strength(self, df: pd.DataFrame) -> float:
        """计算趋势强度"""
        try:
            # 使用ADX指标衡量趋势强度
            adx = talib.ADX(df['high'], df['low'], df['close'])[-1]
            return float(adx) / 100.0  # 归一化到0-1范围
            
        except Exception as e:
            logger.error(f"计算趋势强度时发生错误: {str(e)}")
            return 0.0
            
    def _calculate_support_resistance(
        self, df: pd.DataFrame
    ) -> Tuple[List[float], List[float]]:
        """计算支撑位和阻力位"""
        try:
            # 使用最近的低点作为支撑位
            lows = df['low'].rolling(window=20, center=True).min()
            support_levels = sorted(set(round(x, 2) for x in lows.dropna().tail(3)))
            
            # 使用最近的高点作为阻力位
            highs = df['high'].rolling(window=20, center=True).max()
            resistance_levels = sorted(set(round(x, 2) for x in highs.dropna().tail(3)))
            
            return support_levels, resistance_levels
            
        except Exception as e:
            logger.error(f"计算支撑和阻力位时发生错误: {str(e)}")
            return [], []
            
    def _calculate_technical_score(
        self, df: pd.DataFrame, ma_5: float, ma_10: float, ma_20: float,
        rsi: float, macd: float, macd_signal: float
    ) -> float:
        """计算技术面评分"""
        try:
            score = 50.0  # 基础分数
            
            # 移动平均线评分
            if ma_5 > ma_10 > ma_20:  # 金叉排列
                score += 10
            elif ma_5 < ma_10 < ma_20:  # 死叉排列
                score -= 10
                
            # RSI评分
            if rsi > 70:
                score -= 5  # 超买
            elif rsi < 30:
                score += 5  # 超卖
                
            # MACD评分
            if macd > macd_signal:
                score += 5
            else:
                score -= 5
                
            # 成交量评分
            volume_ma = df['volume'].rolling(window=20).mean()
            if df['volume'].iloc[-1] > volume_ma.iloc[-1]:
                score += 5
                
            return min(max(score, 0), 100)  # 确保分数在0-100范围内
            
        except Exception as e:
            logger.error(f"计算技术面评分时发生错误: {str(e)}")
            return 50.0
            
    def _determine_risk_level(
        self, volatility: float, technical_score: float, trend_strength: float
    ) -> str:
        """确定风险水平"""
        try:
            # 综合考虑波动率、技术评分和趋势强度
            risk_score = (
                volatility * 0.4 +  # 波动率权重
                (100 - technical_score) * 0.3 +  # 技术评分权重
                trend_strength * 0.3  # 趋势强度权重
            )
            
            if risk_score < 30:
                return "低风险"
            elif risk_score < 60:
                return "中等风险"
            else:
                return "高风险"
                
        except Exception as e:
            logger.error(f"确定风险水平时发生错误: {str(e)}")
            return "未知"
            
    def _generate_trading_suggestion(
        self, technical_score: float, risk_level: str, trend: str
    ) -> str:
        """生成交易建议"""
        try:
            if technical_score >= 70 and risk_level != "高风险" and trend == "上升":
                return "建议买入"
            elif technical_score <= 30 and trend == "下降":
                return "建议卖出"
            elif 30 < technical_score < 70:
                return "建议观望"
            else:
                return "需要进一步观察"
                
        except Exception as e:
            logger.error(f"生成交易建议时发生错误: {str(e)}")
            return "无法生成建议"
            
    def save_analysis_results(
        self, db: Session, symbol: str, analysis_results: Dict
    ) -> Optional[StockAnalysis]:
        """保存分析结果到数据库"""
        try:
            stock_analysis = StockAnalysis(
                symbol=symbol,
                analysis_date=datetime.now(),
                ma_5=analysis_results.get('ma_5'),
                ma_10=analysis_results.get('ma_10'),
                ma_20=analysis_results.get('ma_20'),
                rsi_14=analysis_results.get('rsi_14'),
                macd=analysis_results.get('macd'),
                macd_signal=analysis_results.get('macd_signal'),
                macd_hist=analysis_results.get('macd_hist'),
                bollinger_upper=analysis_results.get('bollinger_upper'),
                bollinger_middle=analysis_results.get('bollinger_middle'),
                bollinger_lower=analysis_results.get('bollinger_lower'),
                volatility=analysis_results.get('volatility'),
                atr=analysis_results.get('atr'),
                trend=analysis_results.get('trend'),
                trend_strength=analysis_results.get('trend_strength'),
                support_levels=analysis_results.get('support_levels'),
                resistance_levels=analysis_results.get('resistance_levels'),
                technical_score=analysis_results.get('technical_score'),
                risk_level=analysis_results.get('risk_level'),
                trading_suggestion=analysis_results.get('trading_suggestion')
            )
            
            db.add(stock_analysis)
            db.commit()
            db.refresh(stock_analysis)
            
            return stock_analysis
            
        except Exception as e:
            logger.error(f"保存分析结果时发生错误: {str(e)}")
            db.rollback()
            return None 