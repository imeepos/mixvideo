"""
Security Audit and Monitoring
安全审计和监控
"""

import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from loguru import logger


class AuditEventType(Enum):
    """审计事件类型"""
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    ACCESS_GRANTED = "access_granted"
    ACCESS_DENIED = "access_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CHANGE = "system_change"
    SECURITY_VIOLATION = "security_violation"
    ERROR = "error"


class AuditSeverity(Enum):
    """审计严重级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化审计日志记录器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="AuditLogger")
        
        # 审计配置
        self.audit_config = self.config.get('audit', {
            'enabled': True,
            'log_file': './logs/audit.log',
            'max_file_size_mb': 100,
            'max_files': 10,
            'log_level': 'INFO',
            'include_stack_trace': False,
            'encrypt_logs': False,
            'retention_days': 90
        })
        
        # 审计日志文件
        self.audit_file = Path(self.audit_config['log_file'])
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 审计事件缓存
        self.event_cache = []
        self.cache_size = 100
        
        # 统计信息
        self.stats = {
            'total_events': 0,
            'events_by_type': {},
            'events_by_severity': {},
            'last_event_time': None
        }
        
        self.logger.info("Audit logger initialized")
    
    def log_event(self, event_type: AuditEventType, message: str, 
                  user_id: Optional[str] = None, resource: Optional[str] = None,
                  severity: AuditSeverity = AuditSeverity.MEDIUM,
                  additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        记录审计事件
        
        Args:
            event_type: 事件类型
            message: 事件消息
            user_id: 用户ID
            resource: 资源标识
            severity: 严重级别
            additional_data: 附加数据
            
        Returns:
            是否记录成功
        """
        try:
            if not self.audit_config['enabled']:
                return True
            
            # 创建审计事件
            event = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type.value,
                'severity': severity.value,
                'message': message,
                'user_id': user_id,
                'resource': resource,
                'session_id': self._get_current_session_id(),
                'ip_address': self._get_client_ip(),
                'user_agent': self._get_user_agent(),
                'additional_data': additional_data or {}
            }
            
            # 添加到缓存
            self.event_cache.append(event)
            
            # 限制缓存大小
            if len(self.event_cache) > self.cache_size:
                self.event_cache = self.event_cache[-self.cache_size:]
            
            # 写入日志文件
            self._write_to_log_file(event)
            
            # 更新统计
            self._update_stats(event)
            
            # 检查安全告警
            self._check_security_alerts(event)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to log audit event: {e}")
            return False
    
    def _write_to_log_file(self, event: Dict[str, Any]):
        """写入日志文件"""
        try:
            log_entry = json.dumps(event, ensure_ascii=False, default=str)
            
            with open(self.audit_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
            
            # 检查文件大小并轮转
            self._rotate_log_if_needed()
            
        except Exception as e:
            self.logger.error(f"Failed to write audit log: {e}")
    
    def _rotate_log_if_needed(self):
        """如果需要则轮转日志"""
        try:
            if not self.audit_file.exists():
                return
            
            file_size_mb = self.audit_file.stat().st_size / (1024 * 1024)
            
            if file_size_mb > self.audit_config['max_file_size_mb']:
                # 轮转日志文件
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = self.audit_file.with_suffix(f'.{timestamp}.log')
                
                self.audit_file.rename(backup_file)
                
                # 清理旧文件
                self._cleanup_old_logs()
                
                self.logger.info(f"Audit log rotated: {backup_file}")
            
        except Exception as e:
            self.logger.error(f"Log rotation failed: {e}")
    
    def _cleanup_old_logs(self):
        """清理旧日志文件"""
        try:
            log_dir = self.audit_file.parent
            log_pattern = f"{self.audit_file.stem}.*.log"
            
            log_files = list(log_dir.glob(log_pattern))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 保留最新的文件
            max_files = self.audit_config['max_files']
            if len(log_files) > max_files:
                for old_file in log_files[max_files:]:
                    old_file.unlink()
                    self.logger.info(f"Deleted old audit log: {old_file}")
            
            # 按保留期清理
            retention_days = self.audit_config['retention_days']
            cutoff_time = datetime.now() - timedelta(days=retention_days)
            
            for log_file in log_files:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_time:
                    log_file.unlink()
                    self.logger.info(f"Deleted expired audit log: {log_file}")
            
        except Exception as e:
            self.logger.error(f"Log cleanup failed: {e}")
    
    def _update_stats(self, event: Dict[str, Any]):
        """更新统计信息"""
        try:
            self.stats['total_events'] += 1
            self.stats['last_event_time'] = event['timestamp']
            
            # 按类型统计
            event_type = event['event_type']
            if event_type not in self.stats['events_by_type']:
                self.stats['events_by_type'][event_type] = 0
            self.stats['events_by_type'][event_type] += 1
            
            # 按严重级别统计
            severity = event['severity']
            if severity not in self.stats['events_by_severity']:
                self.stats['events_by_severity'][severity] = 0
            self.stats['events_by_severity'][severity] += 1
            
        except Exception as e:
            self.logger.error(f"Stats update failed: {e}")
    
    def _check_security_alerts(self, event: Dict[str, Any]):
        """检查安全告警"""
        try:
            # 检查高危事件
            if event['severity'] == AuditSeverity.CRITICAL.value:
                self._trigger_security_alert(event, "Critical security event detected")
            
            # 检查登录失败次数
            if event['event_type'] == AuditEventType.LOGIN_FAILED.value:
                self._check_failed_login_threshold(event)
            
            # 检查访问拒绝次数
            if event['event_type'] == AuditEventType.ACCESS_DENIED.value:
                self._check_access_denied_threshold(event)
            
        except Exception as e:
            self.logger.error(f"Security alert check failed: {e}")
    
    def _check_failed_login_threshold(self, event: Dict[str, Any]):
        """检查登录失败阈值"""
        try:
            user_id = event.get('user_id')
            if not user_id:
                return
            
            # 统计最近1小时内的失败次数
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            failed_count = 0
            for cached_event in self.event_cache:
                if (cached_event['event_type'] == AuditEventType.LOGIN_FAILED.value and
                    cached_event.get('user_id') == user_id and
                    datetime.fromisoformat(cached_event['timestamp']) > cutoff_time):
                    failed_count += 1
            
            if failed_count >= 5:  # 阈值
                self._trigger_security_alert(
                    event, 
                    f"Multiple login failures detected for user {user_id}: {failed_count} attempts"
                )
            
        except Exception as e:
            self.logger.error(f"Failed login threshold check failed: {e}")
    
    def _check_access_denied_threshold(self, event: Dict[str, Any]):
        """检查访问拒绝阈值"""
        try:
            user_id = event.get('user_id')
            if not user_id:
                return
            
            # 统计最近30分钟内的拒绝次数
            cutoff_time = datetime.now() - timedelta(minutes=30)
            
            denied_count = 0
            for cached_event in self.event_cache:
                if (cached_event['event_type'] == AuditEventType.ACCESS_DENIED.value and
                    cached_event.get('user_id') == user_id and
                    datetime.fromisoformat(cached_event['timestamp']) > cutoff_time):
                    denied_count += 1
            
            if denied_count >= 10:  # 阈值
                self._trigger_security_alert(
                    event,
                    f"Multiple access denials detected for user {user_id}: {denied_count} attempts"
                )
            
        except Exception as e:
            self.logger.error(f"Access denied threshold check failed: {e}")
    
    def _trigger_security_alert(self, event: Dict[str, Any], alert_message: str):
        """触发安全告警"""
        try:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'alert_type': 'security_alert',
                'message': alert_message,
                'triggering_event': event,
                'severity': 'high'
            }
            
            # 记录告警事件
            self.log_event(
                AuditEventType.SECURITY_VIOLATION,
                alert_message,
                event.get('user_id'),
                severity=AuditSeverity.HIGH,
                additional_data={'alert': alert}
            )
            
            # 发送通知（可以集成邮件、短信等）
            self.logger.warning(f"SECURITY ALERT: {alert_message}")
            
        except Exception as e:
            self.logger.error(f"Security alert trigger failed: {e}")
    
    def _get_current_session_id(self) -> Optional[str]:
        """获取当前会话ID"""
        # 这里可以从上下文或请求中获取会话ID
        return None
    
    def _get_client_ip(self) -> Optional[str]:
        """获取客户端IP地址"""
        # 这里可以从请求中获取IP地址
        return None
    
    def _get_user_agent(self) -> Optional[str]:
        """获取用户代理"""
        # 这里可以从请求中获取User-Agent
        return None
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """获取审计统计信息"""
        return self.stats.copy()
    
    def search_events(self, start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None,
                     event_type: Optional[AuditEventType] = None,
                     user_id: Optional[str] = None,
                     severity: Optional[AuditSeverity] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        搜索审计事件
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            event_type: 事件类型
            user_id: 用户ID
            severity: 严重级别
            limit: 结果限制
            
        Returns:
            匹配的事件列表
        """
        try:
            results = []
            
            # 从缓存中搜索
            for event in self.event_cache:
                if self._event_matches_criteria(
                    event, start_time, end_time, event_type, user_id, severity
                ):
                    results.append(event)
                    
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            self.logger.error(f"Event search failed: {e}")
            return []
    
    def _event_matches_criteria(self, event: Dict[str, Any],
                               start_time: Optional[datetime],
                               end_time: Optional[datetime],
                               event_type: Optional[AuditEventType],
                               user_id: Optional[str],
                               severity: Optional[AuditSeverity]) -> bool:
        """检查事件是否匹配搜索条件"""
        try:
            # 时间范围检查
            event_time = datetime.fromisoformat(event['timestamp'])
            
            if start_time and event_time < start_time:
                return False
            
            if end_time and event_time > end_time:
                return False
            
            # 事件类型检查
            if event_type and event['event_type'] != event_type.value:
                return False
            
            # 用户ID检查
            if user_id and event.get('user_id') != user_id:
                return False
            
            # 严重级别检查
            if severity and event['severity'] != severity.value:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Event criteria check failed: {e}")
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            # 清空缓存
            self.event_cache.clear()
            
            self.logger.info("Audit logger cleanup completed")
        except Exception as e:
            self.logger.error(f"Audit logger cleanup failed: {e}")


class SecurityMonitor:
    """安全监控器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化安全监控器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="SecurityMonitor")
        
        # 监控配置
        self.monitor_config = self.config.get('security_monitor', {
            'enabled': True,
            'check_interval_seconds': 60,
            'threat_detection_enabled': True,
            'anomaly_detection_enabled': True,
            'real_time_alerts': True
        })
        
        # 审计日志记录器
        self.audit_logger = AuditLogger(config)
        
        # 威胁检测规则
        self.threat_rules = []
        
        # 异常检测基线
        self.baseline_metrics = {}
        
        # 监控状态
        self.monitoring_active = False
        
        # 加载威胁检测规则
        self._load_threat_rules()
        
        self.logger.info("Security monitor initialized")
    
    def _load_threat_rules(self):
        """加载威胁检测规则"""
        try:
            # 默认威胁检测规则
            self.threat_rules = [
                {
                    'name': 'brute_force_login',
                    'description': 'Detect brute force login attempts',
                    'condition': 'failed_login_count > 5 in 10 minutes',
                    'severity': 'high',
                    'enabled': True
                },
                {
                    'name': 'privilege_escalation',
                    'description': 'Detect privilege escalation attempts',
                    'condition': 'access_denied_count > 10 in 5 minutes',
                    'severity': 'critical',
                    'enabled': True
                },
                {
                    'name': 'suspicious_activity',
                    'description': 'Detect suspicious user activity',
                    'condition': 'unusual_access_pattern',
                    'severity': 'medium',
                    'enabled': True
                }
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to load threat rules: {e}")
    
    def start_monitoring(self):
        """开始安全监控"""
        try:
            if not self.monitor_config['enabled']:
                self.logger.info("Security monitoring is disabled")
                return
            
            self.monitoring_active = True
            
            # 启动监控循环
            import asyncio
            asyncio.create_task(self._monitoring_loop())
            
            self.logger.info("Security monitoring started")
            
        except Exception as e:
            self.logger.error(f"Failed to start security monitoring: {e}")
    
    def stop_monitoring(self):
        """停止安全监控"""
        try:
            self.monitoring_active = False
            self.logger.info("Security monitoring stopped")
            
        except Exception as e:
            self.logger.error(f"Failed to stop security monitoring: {e}")
    
    async def _monitoring_loop(self):
        """监控循环"""
        import asyncio
        
        while self.monitoring_active:
            try:
                # 威胁检测
                if self.monitor_config['threat_detection_enabled']:
                    await self._run_threat_detection()
                
                # 异常检测
                if self.monitor_config['anomaly_detection_enabled']:
                    await self._run_anomaly_detection()
                
                # 等待下一次检查
                await asyncio.sleep(self.monitor_config['check_interval_seconds'])
                
            except Exception as e:
                self.logger.error(f"Security monitoring loop error: {e}")
                await asyncio.sleep(5)  # 错误时短暂等待
    
    async def _run_threat_detection(self):
        """运行威胁检测"""
        try:
            for rule in self.threat_rules:
                if not rule['enabled']:
                    continue
                
                # 执行威胁检测规则
                threat_detected = await self._evaluate_threat_rule(rule)
                
                if threat_detected:
                    self._handle_threat_detection(rule, threat_detected)
            
        except Exception as e:
            self.logger.error(f"Threat detection failed: {e}")
    
    async def _evaluate_threat_rule(self, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """评估威胁检测规则"""
        try:
            rule_name = rule['name']
            
            if rule_name == 'brute_force_login':
                return await self._check_brute_force_login()
            elif rule_name == 'privilege_escalation':
                return await self._check_privilege_escalation()
            elif rule_name == 'suspicious_activity':
                return await self._check_suspicious_activity()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Threat rule evaluation failed: {e}")
            return None
    
    async def _check_brute_force_login(self) -> Optional[Dict[str, Any]]:
        """检查暴力破解登录"""
        try:
            # 获取最近10分钟的登录失败事件
            cutoff_time = datetime.now() - timedelta(minutes=10)
            
            failed_events = self.audit_logger.search_events(
                start_time=cutoff_time,
                event_type=AuditEventType.LOGIN_FAILED,
                limit=1000
            )
            
            # 按用户统计失败次数
            user_failures = {}
            for event in failed_events:
                user_id = event.get('user_id')
                if user_id:
                    user_failures[user_id] = user_failures.get(user_id, 0) + 1
            
            # 检查是否超过阈值
            for user_id, count in user_failures.items():
                if count > 5:
                    return {
                        'user_id': user_id,
                        'failure_count': count,
                        'time_window': '10 minutes'
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Brute force check failed: {e}")
            return None
    
    async def _check_privilege_escalation(self) -> Optional[Dict[str, Any]]:
        """检查权限提升"""
        try:
            # 获取最近5分钟的访问拒绝事件
            cutoff_time = datetime.now() - timedelta(minutes=5)
            
            denied_events = self.audit_logger.search_events(
                start_time=cutoff_time,
                event_type=AuditEventType.ACCESS_DENIED,
                limit=1000
            )
            
            # 按用户统计拒绝次数
            user_denials = {}
            for event in denied_events:
                user_id = event.get('user_id')
                if user_id:
                    user_denials[user_id] = user_denials.get(user_id, 0) + 1
            
            # 检查是否超过阈值
            for user_id, count in user_denials.items():
                if count > 10:
                    return {
                        'user_id': user_id,
                        'denial_count': count,
                        'time_window': '5 minutes'
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Privilege escalation check failed: {e}")
            return None
    
    async def _check_suspicious_activity(self) -> Optional[Dict[str, Any]]:
        """检查可疑活动"""
        try:
            # 这里可以实现更复杂的异常检测算法
            # 例如：检测异常的访问模式、时间、地理位置等
            
            # 简单示例：检测深夜访问
            current_hour = datetime.now().hour
            if 2 <= current_hour <= 5:  # 凌晨2-5点
                recent_events = self.audit_logger.search_events(
                    start_time=datetime.now() - timedelta(hours=1),
                    limit=100
                )
                
                if len(recent_events) > 10:  # 深夜有较多活动
                    return {
                        'activity_type': 'late_night_access',
                        'event_count': len(recent_events),
                        'time_window': '1 hour'
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Suspicious activity check failed: {e}")
            return None
    
    async def _run_anomaly_detection(self):
        """运行异常检测"""
        try:
            # 收集当前指标
            current_metrics = await self._collect_security_metrics()
            
            # 与基线比较
            anomalies = self._detect_anomalies(current_metrics)
            
            # 处理异常
            for anomaly in anomalies:
                self._handle_anomaly_detection(anomaly)
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
    
    async def _collect_security_metrics(self) -> Dict[str, Any]:
        """收集安全指标"""
        try:
            stats = self.audit_logger.get_audit_stats()
            
            return {
                'total_events': stats['total_events'],
                'events_by_type': stats['events_by_type'],
                'events_by_severity': stats['events_by_severity'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Security metrics collection failed: {e}")
            return {}
    
    def _detect_anomalies(self, current_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测异常"""
        anomalies = []
        
        try:
            # 简单的异常检测逻辑
            # 实际应用中可以使用更复杂的机器学习算法
            
            if not self.baseline_metrics:
                # 如果没有基线，将当前指标作为基线
                self.baseline_metrics = current_metrics.copy()
                return anomalies
            
            # 检查事件数量异常
            current_total = current_metrics.get('total_events', 0)
            baseline_total = self.baseline_metrics.get('total_events', 0)
            
            if current_total > baseline_total * 2:  # 事件数量翻倍
                anomalies.append({
                    'type': 'event_volume_spike',
                    'description': 'Unusual increase in audit events',
                    'current_value': current_total,
                    'baseline_value': baseline_total,
                    'severity': 'medium'
                })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def _handle_threat_detection(self, rule: Dict[str, Any], threat_data: Dict[str, Any]):
        """处理威胁检测"""
        try:
            message = f"Threat detected: {rule['name']} - {rule['description']}"
            
            self.audit_logger.log_event(
                AuditEventType.SECURITY_VIOLATION,
                message,
                threat_data.get('user_id'),
                severity=AuditSeverity.HIGH,
                additional_data={
                    'rule': rule,
                    'threat_data': threat_data
                }
            )
            
            self.logger.warning(f"THREAT DETECTED: {message}")
            
        except Exception as e:
            self.logger.error(f"Threat detection handling failed: {e}")
    
    def _handle_anomaly_detection(self, anomaly: Dict[str, Any]):
        """处理异常检测"""
        try:
            message = f"Anomaly detected: {anomaly['type']} - {anomaly['description']}"
            
            self.audit_logger.log_event(
                AuditEventType.SECURITY_VIOLATION,
                message,
                severity=AuditSeverity.MEDIUM,
                additional_data={'anomaly': anomaly}
            )
            
            self.logger.warning(f"ANOMALY DETECTED: {message}")
            
        except Exception as e:
            self.logger.error(f"Anomaly detection handling failed: {e}")
    
    def cleanup(self):
        """清理资源"""
        try:
            self.stop_monitoring()
            self.audit_logger.cleanup()
            self.logger.info("Security monitor cleanup completed")
        except Exception as e:
            self.logger.error(f"Security monitor cleanup failed: {e}")
