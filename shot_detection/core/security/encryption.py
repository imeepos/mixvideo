"""
Encryption and Secure Storage
加密和安全存储
"""

import os
import json
import base64
import secrets
from pathlib import Path
from typing import Dict, Any, Optional, Union, Tuple
from datetime import datetime
from loguru import logger

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化加密管理器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="EncryptionManager")
        
        if not CRYPTO_AVAILABLE:
            self.logger.warning("Cryptography library not available, encryption disabled")
            return
        
        # 加密配置
        self.encryption_config = self.config.get('encryption', {
            'algorithm': 'fernet',  # fernet, aes
            'key_derivation': 'pbkdf2',
            'key_iterations': 100000,
            'key_length': 32,
            'use_hardware_rng': True
        })
        
        # 密钥存储
        self.keys = {}
        
        # 主密钥
        self.master_key = None
        
        # 初始化加密
        self._initialize_encryption()
        
        self.logger.info("Encryption manager initialized")
    
    def _initialize_encryption(self):
        """初始化加密"""
        try:
            # 生成或加载主密钥
            self._load_or_generate_master_key()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize encryption: {e}")
    
    def _load_or_generate_master_key(self):
        """加载或生成主密钥"""
        try:
            key_file = Path(self.config.get('master_key_file', './data/master.key'))
            key_file.parent.mkdir(parents=True, exist_ok=True)
            
            if key_file.exists():
                # 加载现有密钥
                with open(key_file, 'rb') as f:
                    self.master_key = f.read()
                self.logger.info("Master key loaded")
            else:
                # 生成新密钥
                self.master_key = Fernet.generate_key()
                
                # 保存密钥
                with open(key_file, 'wb') as f:
                    f.write(self.master_key)
                
                # 设置文件权限（仅所有者可读写）
                os.chmod(key_file, 0o600)
                
                self.logger.info("New master key generated and saved")
                
        except Exception as e:
            self.logger.error(f"Failed to load/generate master key: {e}")
            raise
    
    def derive_key(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        从密码派生密钥
        
        Args:
            password: 密码
            salt: 盐值（如果为None则生成新的）
            
        Returns:
            (密钥, 盐值)
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        try:
            if salt is None:
                salt = os.urandom(16)
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=self.encryption_config['key_length'],
                salt=salt,
                iterations=self.encryption_config['key_iterations']
            )
            
            key = kdf.derive(password.encode('utf-8'))
            return key, salt
            
        except Exception as e:
            self.logger.error(f"Key derivation failed: {e}")
            raise
    
    def encrypt_data(self, data: Union[str, bytes], key: Optional[bytes] = None) -> Dict[str, Any]:
        """
        加密数据
        
        Args:
            data: 要加密的数据
            key: 加密密钥（如果为None则使用主密钥）
            
        Returns:
            加密结果
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        try:
            if key is None:
                key = self.master_key
            
            # 转换为字节
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            # 使用Fernet加密
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(data)
            
            return {
                'success': True,
                'encrypted_data': base64.b64encode(encrypted_data).decode('utf-8'),
                'algorithm': 'fernet',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def decrypt_data(self, encrypted_data: str, key: Optional[bytes] = None) -> Dict[str, Any]:
        """
        解密数据
        
        Args:
            encrypted_data: 加密的数据（base64编码）
            key: 解密密钥（如果为None则使用主密钥）
            
        Returns:
            解密结果
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        try:
            if key is None:
                key = self.master_key
            
            # 解码base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # 使用Fernet解密
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_bytes)
            
            return {
                'success': True,
                'decrypted_data': decrypted_data.decode('utf-8'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None, 
                    key: Optional[bytes] = None) -> Dict[str, Any]:
        """
        加密文件
        
        Args:
            file_path: 源文件路径
            output_path: 输出文件路径
            key: 加密密钥
            
        Returns:
            加密结果
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        try:
            if key is None:
                key = self.master_key
            
            if output_path is None:
                output_path = f"{file_path}.encrypted"
            
            # 读取文件
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # 加密数据
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(file_data)
            
            # 写入加密文件
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            self.logger.info(f"File encrypted: {file_path} -> {output_path}")
            
            return {
                'success': True,
                'input_file': file_path,
                'output_file': output_path,
                'file_size': len(encrypted_data)
            }
            
        except Exception as e:
            self.logger.error(f"File encryption failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None,
                    key: Optional[bytes] = None) -> Dict[str, Any]:
        """
        解密文件
        
        Args:
            encrypted_file_path: 加密文件路径
            output_path: 输出文件路径
            key: 解密密钥
            
        Returns:
            解密结果
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        try:
            if key is None:
                key = self.master_key
            
            if output_path is None:
                if encrypted_file_path.endswith('.encrypted'):
                    output_path = encrypted_file_path[:-10]  # 移除.encrypted后缀
                else:
                    output_path = f"{encrypted_file_path}.decrypted"
            
            # 读取加密文件
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # 解密数据
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # 写入解密文件
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            self.logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            
            return {
                'success': True,
                'input_file': encrypted_file_path,
                'output_file': output_path,
                'file_size': len(decrypted_data)
            }
            
        except Exception as e:
            self.logger.error(f"File decryption failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_key_pair(self) -> Dict[str, Any]:
        """
        生成RSA密钥对
        
        Returns:
            密钥对信息
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError("Cryptography library not available")
        
        try:
            # 生成私钥
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # 获取公钥
            public_key = private_key.public_key()
            
            # 序列化私钥
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # 序列化公钥
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return {
                'success': True,
                'private_key': private_pem.decode('utf-8'),
                'public_key': public_pem.decode('utf-8'),
                'key_size': 2048,
                'algorithm': 'RSA'
            }
            
        except Exception as e:
            self.logger.error(f"Key pair generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def hash_data(self, data: Union[str, bytes], algorithm: str = 'sha256') -> str:
        """
        哈希数据
        
        Args:
            data: 要哈希的数据
            algorithm: 哈希算法
            
        Returns:
            哈希值（十六进制）
        """
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if algorithm == 'sha256':
                digest = hashes.Hash(hashes.SHA256())
            elif algorithm == 'sha512':
                digest = hashes.Hash(hashes.SHA512())
            elif algorithm == 'md5':
                digest = hashes.Hash(hashes.MD5())
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            digest.update(data)
            return digest.finalize().hex()
            
        except Exception as e:
            self.logger.error(f"Hashing failed: {e}")
            raise
    
    def cleanup(self):
        """清理资源"""
        try:
            # 清除内存中的密钥
            if self.master_key:
                self.master_key = None
            
            self.keys.clear()
            
            self.logger.info("Encryption manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Encryption cleanup failed: {e}")


class SecureStorage:
    """安全存储"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化安全存储
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        self.logger = logger.bind(component="SecureStorage")
        
        # 存储配置
        self.storage_config = self.config.get('secure_storage', {
            'storage_dir': './data/secure',
            'encrypt_data': True,
            'compress_data': False,
            'backup_enabled': True,
            'backup_interval_hours': 24
        })
        
        # 存储目录
        self.storage_dir = Path(self.storage_config['storage_dir'])
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 加密管理器
        self.encryption_manager = EncryptionManager(config) if CRYPTO_AVAILABLE else None
        
        # 存储索引
        self.storage_index = {}
        
        # 加载索引
        self._load_storage_index()
        
        self.logger.info("Secure storage initialized")
    
    def _load_storage_index(self):
        """加载存储索引"""
        try:
            index_file = self.storage_dir / 'index.json'
            
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    self.storage_index = json.load(f)
            
        except Exception as e:
            self.logger.error(f"Failed to load storage index: {e}")
    
    def _save_storage_index(self):
        """保存存储索引"""
        try:
            index_file = self.storage_dir / 'index.json'
            
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(self.storage_index, f, indent=2, ensure_ascii=False, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to save storage index: {e}")
    
    def store_data(self, key: str, data: Any, encrypt: Optional[bool] = None) -> bool:
        """
        存储数据
        
        Args:
            key: 存储键
            data: 要存储的数据
            encrypt: 是否加密（None则使用配置）
            
        Returns:
            是否存储成功
        """
        try:
            if encrypt is None:
                encrypt = self.storage_config['encrypt_data']
            
            # 序列化数据
            if isinstance(data, (dict, list)):
                serialized_data = json.dumps(data, ensure_ascii=False, default=str)
            else:
                serialized_data = str(data)
            
            # 加密数据
            if encrypt and self.encryption_manager:
                result = self.encryption_manager.encrypt_data(serialized_data)
                if not result['success']:
                    return False
                
                stored_data = {
                    'encrypted': True,
                    'data': result['encrypted_data'],
                    'algorithm': result['algorithm']
                }
            else:
                stored_data = {
                    'encrypted': False,
                    'data': serialized_data
                }
            
            # 保存到文件
            file_path = self.storage_dir / f"{key}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(stored_data, f, indent=2, ensure_ascii=False)
            
            # 更新索引
            self.storage_index[key] = {
                'file_path': str(file_path),
                'encrypted': encrypt,
                'created_at': datetime.now().isoformat(),
                'size': file_path.stat().st_size
            }
            
            self._save_storage_index()
            
            self.logger.info(f"Data stored: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store data {key}: {e}")
            return False
    
    def retrieve_data(self, key: str) -> Optional[Any]:
        """
        检索数据
        
        Args:
            key: 存储键
            
        Returns:
            存储的数据
        """
        try:
            if key not in self.storage_index:
                return None
            
            file_path = Path(self.storage_index[key]['file_path'])
            if not file_path.exists():
                return None
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                stored_data = json.load(f)
            
            # 解密数据
            if stored_data.get('encrypted', False):
                if not self.encryption_manager:
                    self.logger.error("Encryption manager not available for decryption")
                    return None
                
                result = self.encryption_manager.decrypt_data(stored_data['data'])
                if not result['success']:
                    return None
                
                data = result['decrypted_data']
            else:
                data = stored_data['data']
            
            # 尝试反序列化JSON
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve data {key}: {e}")
            return None
    
    def delete_data(self, key: str) -> bool:
        """
        删除数据
        
        Args:
            key: 存储键
            
        Returns:
            是否删除成功
        """
        try:
            if key not in self.storage_index:
                return False
            
            file_path = Path(self.storage_index[key]['file_path'])
            if file_path.exists():
                file_path.unlink()
            
            del self.storage_index[key]
            self._save_storage_index()
            
            self.logger.info(f"Data deleted: {key}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete data {key}: {e}")
            return False
    
    def list_keys(self) -> List[str]:
        """列出所有存储键"""
        return list(self.storage_index.keys())
    
    def get_storage_info(self) -> Dict[str, Any]:
        """获取存储信息"""
        try:
            total_size = sum(info['size'] for info in self.storage_index.values())
            encrypted_count = sum(1 for info in self.storage_index.values() if info['encrypted'])
            
            return {
                'total_items': len(self.storage_index),
                'total_size_bytes': total_size,
                'encrypted_items': encrypted_count,
                'storage_directory': str(self.storage_dir),
                'encryption_enabled': self.storage_config['encrypt_data']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get storage info: {e}")
            return {}
    
    def cleanup(self):
        """清理资源"""
        try:
            self._save_storage_index()
            
            if self.encryption_manager:
                self.encryption_manager.cleanup()
            
            self.logger.info("Secure storage cleanup completed")
        except Exception as e:
            self.logger.error(f"Secure storage cleanup failed: {e}")

    def backup_storage(self) -> bool:
        """
        备份存储数据

        Returns:
            是否备份成功
        """
        try:
            if not self.storage_config['backup_enabled']:
                return True

            backup_dir = self.storage_dir / 'backups'
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_dir / f"backup_{timestamp}.tar.gz"

            import tarfile

            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(self.storage_dir, arcname='storage',
                       filter=lambda x: None if 'backups' in x.name else x)

            self.logger.info(f"Storage backup created: {backup_file}")
            return True

        except Exception as e:
            self.logger.error(f"Storage backup failed: {e}")
            return False
