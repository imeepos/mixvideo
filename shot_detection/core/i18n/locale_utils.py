"""
Locale Utilities
本地化工具
"""

import locale
import datetime
import re
from typing import Dict, Any, Optional, Union
from loguru import logger


class LocaleUtils:
    """本地化工具类"""
    
    def __init__(self, language_code: Optional[str] = None):
        """
        初始化本地化工具
        
        Args:
            language_code: 语言代码
        """
        self.logger = logger.bind(component="LocaleUtils")
        self.language_code = language_code or self._detect_system_locale()
        
        # 语言配置
        self.locale_config = {
            'zh_CN': {
                'decimal_separator': '.',
                'thousands_separator': ',',
                'date_format': '%Y年%m月%d日',
                'time_format': '%H:%M:%S',
                'datetime_format': '%Y年%m月%d日 %H:%M:%S',
                'currency_symbol': '¥',
                'currency_format': '¥{amount}',
                'number_format': '{:,.2f}',
                'file_size_units': ['字节', 'KB', 'MB', 'GB', 'TB'],
                'time_units': ['秒', '分钟', '小时', '天'],
                'relative_time': {
                    'just_now': '刚刚',
                    'minutes_ago': '{minutes}分钟前',
                    'hours_ago': '{hours}小时前',
                    'days_ago': '{days}天前',
                    'weeks_ago': '{weeks}周前',
                    'months_ago': '{months}个月前',
                    'years_ago': '{years}年前'
                }
            },
            'en_US': {
                'decimal_separator': '.',
                'thousands_separator': ',',
                'date_format': '%m/%d/%Y',
                'time_format': '%I:%M:%S %p',
                'datetime_format': '%m/%d/%Y %I:%M:%S %p',
                'currency_symbol': '$',
                'currency_format': '${amount}',
                'number_format': '{:,.2f}',
                'file_size_units': ['bytes', 'KB', 'MB', 'GB', 'TB'],
                'time_units': ['second', 'minute', 'hour', 'day'],
                'relative_time': {
                    'just_now': 'just now',
                    'minutes_ago': '{minutes} minutes ago',
                    'hours_ago': '{hours} hours ago',
                    'days_ago': '{days} days ago',
                    'weeks_ago': '{weeks} weeks ago',
                    'months_ago': '{months} months ago',
                    'years_ago': '{years} years ago'
                }
            }
        }
        
        self.logger.info(f"Locale utils initialized for: {self.language_code}")
    
    def _detect_system_locale(self) -> str:
        """检测系统本地化设置"""
        try:
            system_locale = locale.getdefaultlocale()[0]
            
            if system_locale:
                if system_locale.startswith('zh'):
                    return 'zh_CN'
                elif system_locale.startswith('en'):
                    return 'en_US'
            
            return 'en_US'  # 默认
            
        except Exception as e:
            self.logger.error(f"Failed to detect system locale: {e}")
            return 'en_US'
    
    def set_language(self, language_code: str):
        """
        设置语言
        
        Args:
            language_code: 语言代码
        """
        self.language_code = language_code
        self.logger.info(f"Locale language set to: {language_code}")
    
    def get_locale_config(self) -> Dict[str, Any]:
        """获取当前语言的本地化配置"""
        return self.locale_config.get(self.language_code, self.locale_config['en_US'])
    
    def format_number(self, number: Union[int, float], decimal_places: int = 2) -> str:
        """
        格式化数字
        
        Args:
            number: 数字
            decimal_places: 小数位数
            
        Returns:
            格式化后的数字字符串
        """
        try:
            config = self.get_locale_config()
            
            if isinstance(number, int):
                return f"{number:,}"
            else:
                format_str = f"{{:,.{decimal_places}f}}"
                return format_str.format(number)
                
        except Exception as e:
            self.logger.error(f"Failed to format number: {e}")
            return str(number)
    
    def format_currency(self, amount: Union[int, float]) -> str:
        """
        格式化货币
        
        Args:
            amount: 金额
            
        Returns:
            格式化后的货币字符串
        """
        try:
            config = self.get_locale_config()
            formatted_amount = self.format_number(amount, 2)
            
            return config['currency_format'].format(amount=formatted_amount)
            
        except Exception as e:
            self.logger.error(f"Failed to format currency: {e}")
            return str(amount)
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        Args:
            size_bytes: 字节数
            
        Returns:
            格式化后的文件大小字符串
        """
        try:
            config = self.get_locale_config()
            units = config['file_size_units']
            
            if size_bytes == 0:
                return f"0 {units[0]}"
            
            size = float(size_bytes)
            unit_index = 0
            
            while size >= 1024 and unit_index < len(units) - 1:
                size /= 1024
                unit_index += 1
            
            if unit_index == 0:
                return f"{int(size)} {units[unit_index]}"
            else:
                return f"{size:.1f} {units[unit_index]}"
                
        except Exception as e:
            self.logger.error(f"Failed to format file size: {e}")
            return f"{size_bytes} bytes"
    
    def format_duration(self, seconds: Union[int, float]) -> str:
        """
        格式化时长
        
        Args:
            seconds: 秒数
            
        Returns:
            格式化后的时长字符串
        """
        try:
            config = self.get_locale_config()
            time_units = config['time_units']
            
            if seconds < 60:
                return f"{int(seconds)} {time_units[0]}"
            elif seconds < 3600:
                minutes = int(seconds // 60)
                remaining_seconds = int(seconds % 60)
                if remaining_seconds > 0:
                    return f"{minutes} {time_units[1]} {remaining_seconds} {time_units[0]}"
                else:
                    return f"{minutes} {time_units[1]}"
            elif seconds < 86400:
                hours = int(seconds // 3600)
                remaining_minutes = int((seconds % 3600) // 60)
                if remaining_minutes > 0:
                    return f"{hours} {time_units[2]} {remaining_minutes} {time_units[1]}"
                else:
                    return f"{hours} {time_units[2]}"
            else:
                days = int(seconds // 86400)
                remaining_hours = int((seconds % 86400) // 3600)
                if remaining_hours > 0:
                    return f"{days} {time_units[3]} {remaining_hours} {time_units[2]}"
                else:
                    return f"{days} {time_units[3]}"
                    
        except Exception as e:
            self.logger.error(f"Failed to format duration: {e}")
            return f"{seconds}s"
    
    def format_date(self, date: datetime.date) -> str:
        """
        格式化日期
        
        Args:
            date: 日期对象
            
        Returns:
            格式化后的日期字符串
        """
        try:
            config = self.get_locale_config()
            return date.strftime(config['date_format'])
            
        except Exception as e:
            self.logger.error(f"Failed to format date: {e}")
            return str(date)
    
    def format_time(self, time: datetime.time) -> str:
        """
        格式化时间
        
        Args:
            time: 时间对象
            
        Returns:
            格式化后的时间字符串
        """
        try:
            config = self.get_locale_config()
            return time.strftime(config['time_format'])
            
        except Exception as e:
            self.logger.error(f"Failed to format time: {e}")
            return str(time)
    
    def format_datetime(self, dt: datetime.datetime) -> str:
        """
        格式化日期时间
        
        Args:
            dt: 日期时间对象
            
        Returns:
            格式化后的日期时间字符串
        """
        try:
            config = self.get_locale_config()
            return dt.strftime(config['datetime_format'])
            
        except Exception as e:
            self.logger.error(f"Failed to format datetime: {e}")
            return str(dt)
    
    def format_relative_time(self, dt: datetime.datetime) -> str:
        """
        格式化相对时间
        
        Args:
            dt: 日期时间对象
            
        Returns:
            相对时间字符串
        """
        try:
            config = self.get_locale_config()
            relative_time_config = config['relative_time']
            
            now = datetime.datetime.now()
            diff = now - dt
            
            total_seconds = diff.total_seconds()
            
            if total_seconds < 60:
                return relative_time_config['just_now']
            elif total_seconds < 3600:
                minutes = int(total_seconds // 60)
                return relative_time_config['minutes_ago'].format(minutes=minutes)
            elif total_seconds < 86400:
                hours = int(total_seconds // 3600)
                return relative_time_config['hours_ago'].format(hours=hours)
            elif total_seconds < 604800:  # 7 days
                days = int(total_seconds // 86400)
                return relative_time_config['days_ago'].format(days=days)
            elif total_seconds < 2629746:  # 30.44 days (average month)
                weeks = int(total_seconds // 604800)
                return relative_time_config['weeks_ago'].format(weeks=weeks)
            elif total_seconds < 31556952:  # 365.24 days (average year)
                months = int(total_seconds // 2629746)
                return relative_time_config['months_ago'].format(months=months)
            else:
                years = int(total_seconds // 31556952)
                return relative_time_config['years_ago'].format(years=years)
                
        except Exception as e:
            self.logger.error(f"Failed to format relative time: {e}")
            return str(dt)
    
    def parse_number(self, number_str: str) -> Optional[float]:
        """
        解析数字字符串
        
        Args:
            number_str: 数字字符串
            
        Returns:
            解析后的数字，失败返回None
        """
        try:
            config = self.get_locale_config()
            
            # 移除千位分隔符
            cleaned = number_str.replace(config['thousands_separator'], '')
            
            # 替换小数分隔符
            if config['decimal_separator'] != '.':
                cleaned = cleaned.replace(config['decimal_separator'], '.')
            
            return float(cleaned)
            
        except Exception as e:
            self.logger.error(f"Failed to parse number '{number_str}': {e}")
            return None
    
    def parse_currency(self, currency_str: str) -> Optional[float]:
        """
        解析货币字符串
        
        Args:
            currency_str: 货币字符串
            
        Returns:
            解析后的金额，失败返回None
        """
        try:
            config = self.get_locale_config()
            
            # 移除货币符号
            cleaned = currency_str.replace(config['currency_symbol'], '').strip()
            
            return self.parse_number(cleaned)
            
        except Exception as e:
            self.logger.error(f"Failed to parse currency '{currency_str}': {e}")
            return None
    
    def parse_file_size(self, size_str: str) -> Optional[int]:
        """
        解析文件大小字符串
        
        Args:
            size_str: 文件大小字符串
            
        Returns:
            解析后的字节数，失败返回None
        """
        try:
            config = self.get_locale_config()
            units = config['file_size_units']
            
            # 使用正则表达式解析
            pattern = r'([\d.,]+)\s*(\w+)'
            match = re.match(pattern, size_str.strip())
            
            if not match:
                return None
            
            number_str, unit_str = match.groups()
            
            # 解析数字
            number = self.parse_number(number_str)
            if number is None:
                return None
            
            # 查找单位
            unit_index = -1
            for i, unit in enumerate(units):
                if unit_str.lower() == unit.lower():
                    unit_index = i
                    break
            
            if unit_index == -1:
                # 尝试英文单位
                english_units = ['bytes', 'kb', 'mb', 'gb', 'tb']
                for i, unit in enumerate(english_units):
                    if unit_str.lower() == unit:
                        unit_index = i
                        break
            
            if unit_index == -1:
                return None
            
            # 计算字节数
            return int(number * (1024 ** unit_index))
            
        except Exception as e:
            self.logger.error(f"Failed to parse file size '{size_str}': {e}")
            return None
    
    def get_decimal_separator(self) -> str:
        """获取小数分隔符"""
        config = self.get_locale_config()
        return config['decimal_separator']
    
    def get_thousands_separator(self) -> str:
        """获取千位分隔符"""
        config = self.get_locale_config()
        return config['thousands_separator']
    
    def get_currency_symbol(self) -> str:
        """获取货币符号"""
        config = self.get_locale_config()
        return config['currency_symbol']
    
    def is_rtl_language(self) -> bool:
        """检查当前语言是否为从右到左"""
        rtl_languages = ['ar', 'he', 'fa', 'ur']
        return any(self.language_code.startswith(lang) for lang in rtl_languages)
    
    def get_text_direction(self) -> str:
        """获取文本方向"""
        return 'rtl' if self.is_rtl_language() else 'ltr'
    
    def sort_strings(self, strings: list, reverse: bool = False) -> list:
        """
        按本地化规则排序字符串
        
        Args:
            strings: 字符串列表
            reverse: 是否逆序
            
        Returns:
            排序后的字符串列表
        """
        try:
            # 设置本地化排序
            if self.language_code == 'zh_CN':
                # 中文按拼音排序
                import pypinyin
                return sorted(strings, 
                            key=lambda x: pypinyin.lazy_pinyin(x), 
                            reverse=reverse)
            else:
                # 其他语言按字母排序
                return sorted(strings, reverse=reverse)
                
        except ImportError:
            # 如果没有pypinyin，使用默认排序
            return sorted(strings, reverse=reverse)
        except Exception as e:
            self.logger.error(f"Failed to sort strings: {e}")
            return strings
    
    def cleanup(self):
        """清理资源"""
        self.logger.info("Locale utils cleanup completed")
