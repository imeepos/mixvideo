
def run_ffmpeg_safe(cmd, timeout=300):
    """安全运行FFmpeg命令，处理编码问题"""
    import subprocess
    
    try:
        # 方法1: UTF-8编码
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            timeout=timeout
        )
        return result
        
    except UnicodeDecodeError:
        # 方法2: 二进制模式 + 手动解码
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout
            )
            
            # 手动解码，忽略错误
            stderr_text = result.stderr.decode('utf-8', errors='ignore') if result.stderr else ""
            stdout_text = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ""
            
            # 创建模拟result对象
            class SafeResult:
                def __init__(self, returncode, stderr, stdout):
                    self.returncode = returncode
                    self.stderr = stderr
                    self.stdout = stdout
            
            return SafeResult(result.returncode, stderr_text, stdout_text)
            
        except Exception as e:
            # 方法3: 最后的备用方案
            class ErrorResult:
                def __init__(self, error):
                    self.returncode = 1
                    self.stderr = f"编码错误: {error}"
                    self.stdout = ""
            
            return ErrorResult(str(e))
    
    except Exception as e:
        # 通用错误处理
        class ErrorResult:
            def __init__(self, error):
                self.returncode = 1
                self.stderr = f"执行错误: {error}"
                self.stdout = ""
        
        return ErrorResult(str(e))
