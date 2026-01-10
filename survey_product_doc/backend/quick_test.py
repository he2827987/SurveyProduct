#!/usr/bin/env python3
"""
快速测试脚本 - 验证标签功能修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """测试导入是否正常"""
    try:
        # 测试标签模型导入
        from backend.app.models.tag import Tag, question_tags
        print("✅ 标签模型导入成功")
        
        # 测试问题模型导入
        from backend.app.models.question import Question
        print("✅ 问题模型导入成功")
        
        # 测试标签API导入
        from backend.app.api.tag_api import router as tag_router
        print("✅ 标签API导入成功")
        
        # 测试标签模式导入
        from backend.app.schemas.tag import TagCreate, TagResponse
        print("✅ 标签模式导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_table_definition():
    """测试表定义是否正常"""
    try:
        from backend.app.models.tag import question_tags
        
        # 检查表定义
        print(f"✅ 关联表名称: {question_tags.name}")
        print(f"✅ 关联表列数: {len(question_tags.columns)}")
        
        return True
    except Exception as e:
        print(f"❌ 表定义测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始快速测试...\n")
    
    # 测试导入
    imports_ok = test_imports()
    
    if imports_ok:
        # 测试表定义
        table_ok = test_table_definition()
        
        print("\n" + "="*50)
        print("📊 测试结果:")
        print(f"   导入测试: {'✅ 通过' if imports_ok else '❌ 失败'}")
        print(f"   表定义测试: {'✅ 通过' if table_ok else '❌ 失败'}")
        
        if imports_ok and table_ok:
            print("\n🎉 标签功能修复成功！")
            print("   现在可以启动后端服务并测试标签筛选功能了。")
        else:
            print("\n⚠️  仍有问题需要解决。")
    else:
        print("\n❌ 导入测试失败，请检查代码。")

if __name__ == "__main__":
    main()
