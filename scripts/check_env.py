#!/usr/bin/env python3
"""
环境变量配置脚本
用于检查和设置必要的环境变量
"""

import os
import sys
from typing import Dict, Any

def check_required_env_vars() -> Dict[str, str]:
    """检查必需的环境变量"""
    required_vars = {
        'DATABASE_URL': '数据库连接字符串',
        'SECRET_KEY': 'JWT密钥',
        'OPENROUTER_API_KEY': 'OpenRouter API密钥',
        'ENVIRONMENT': '环境标识 (development/production)'
    }
    
    missing_vars = {}
    present_vars = {}
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if not value:
            missing_vars[var_name] = description
        else:
            # 对于敏感信息，只显示前几个字符
            if 'KEY' in var_name or 'SECRET' in var_name:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
            else:
                display_value = value
            present_vars[var_name] = display_value
    
    return present_vars, missing_vars

def set_development_defaults():
    """设置开发环境的默认值（仅在没有设置时）"""
    defaults = {
        'ENVIRONMENT': 'development',
        'DATABASE_URL': 'postgresql://localhost:5432/survey_db',
        'SECRET_KEY': 'development-secret-key-change-in-production'
    }
    
    for key, value in defaults.items():
        if not os.getenv(key):
            os.environ[key] = value
            print(f"✅ 设置默认环境变量: {key}")

def validate_environment():
    """验证环境配置"""
    print("🔍 检查环境变量配置...")
    print("=" * 50)
    
    present_vars, missing_vars = check_required_env_vars()
    
    # 显示已设置的环境变量
    if present_vars:
        print("✅ 已设置的环境变量:")
        for var_name, value in present_vars.items():
            print(f"   {var_name}: {value}")
    
    # 显示缺失的环境变量
    if missing_vars:
        print("\n❌ 缺失的环境变量:")
        for var_name, description in missing_vars.items():
            print(f"   {var_name}: {description}")
        
        print("\n⚠️  请设置缺失的环境变量后再运行应用")
        return False
    
    # 检查特定环境的配置
    env = os.getenv('ENVIRONMENT', 'development')
    if env == 'production':
        prod_required = ['DATABASE_URL', 'SECRET_KEY', 'OPENROUTER_API_KEY']
        prod_missing = [var for var in prod_required if not os.getenv(var)]
        if prod_missing:
            print(f"\n❌ 生产环境缺少必需变量: {', '.join(prod_missing)}")
            return False
    
    print("\n✅ 环境变量配置检查通过")
    return True

def setup_production_environment():
    """生产环境配置检查"""
    if os.getenv('ENVIRONMENT') == 'production':
        print("🚀 检测到生产环境，执行生产环境配置检查...")
        
        # 检查数据库URL是否使用SSL
        db_url = os.getenv('DATABASE_URL', '')
        if 'postgresql' in db_url and 'sslmode=' not in db_url:
            print("⚠️  警告: 生产环境数据库连接应使用SSL")
        
        # 检查SECRET_KEY强度
        secret_key = os.getenv('SECRET_KEY', '')
        if len(secret_key) < 32:
            print("⚠️  警告: 生产环境SECRET_KEY长度应至少32个字符")
        
        # 检查API密钥是否为默认值
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        if not api_key or api_key.startswith('sk-or-v1-') == False:
            print("❌ 错误: 生产环境必须设置有效的OPENROUTER_API_KEY")
            return False
        
        print("✅ 生产环境配置检查通过")
    
    return True

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'check':
            if not validate_environment():
                sys.exit(1)
        
        elif command == 'setup-dev':
            set_development_defaults()
            if not validate_environment():
                sys.exit(1)
        
        elif command == 'setup-prod':
            if not validate_environment():
                sys.exit(1)
            if not setup_production_environment():
                sys.exit(1)
        
        else:
            print("用法:")
            print("  python check_env.py check      # 检查环境变量")
            print("  python check_env.py setup-dev  # 设置开发环境默认值")
            print("  python check_env.py setup-prod # 生产环境配置检查")
            sys.exit(1)
    else:
        # 默认执行检查
        if not validate_environment():
            sys.exit(1)

if __name__ == "__main__":
    main()