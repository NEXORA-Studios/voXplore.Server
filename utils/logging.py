import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

class LoggerFactory:
    """
    日志组件，支持同时输出到文件和终端
    """
    
    def __init__(self, name: str, log_dir: str = "logs", log_level: int = logging.INFO):
        """
        初始化日志组件
        
        :param name: 日志名称
        :param log_dir: 日志目录，默认为项目根目录下的logs文件夹
        :param log_level: 日志级别，默认为INFO
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # 确保日志目录存在
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 文件日志处理器 - 按大小滚动，最多保留5个文件，每个文件最大 128 MB
        file_handler = RotatingFileHandler(
            filename=f"{log_dir}/server.log",
            maxBytes=128*1024*1024,  # 128 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        
        # 控制台日志处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # 清空日志文件
        open(f"{log_dir}/server.log", 'w').close()
    
    def debug(self, msg: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(msg, *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """记录常规信息"""
        self.logger.info(msg, *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """记录警告信息"""
        self.logger.warning(msg, *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """记录错误信息"""
        self.logger.error(msg, *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """记录严重错误信息"""
        self.logger.critical(msg, *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        """记录异常信息，包含堆栈跟踪"""
        self.logger.exception(msg, *args, **kwargs)

# 全局日志实例
logger = LoggerFactory("app")