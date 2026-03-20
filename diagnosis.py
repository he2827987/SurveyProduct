#!/usr/bin/env python3
"""
深度诊断脚本 - 检查页面DOM结构和错误
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# 初始化浏览器
options = webdriver.ChromeOptions()
options.add_argument('--window-size=1280,720')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    print("=" * 60)
    print("开始深度诊断")
    print("=" * 60)
    
    # 访问登录页面
    print("\n【检查登录页面】")
    driver.get("http://localhost:3000/login")
    time.sleep(3)
    
    # 获取页面HTML
    html = driver.page_source
    print(f"\n页面HTML长度: {len(html)} 字符")
    
    # 获取页面标题
    title = driver.title
    print(f"页面标题: {title}")
    
    # 查找所有input元素
    print("\n【查找所有input元素】")
    inputs = driver.find_elements(By.TAG_NAME, 'input')
    print(f"找到 {len(inputs)} 个input元素")
    
    for i, inp in enumerate(inputs[:5], 1):
        try:
            input_type = inp.get_attribute('type') or 'text'
            input_placeholder = inp.get_attribute('placeholder') or 'None'
            input_class = inp.get_attribute('class') or 'None'
            print(f"  {i}. type={input_type}, placeholder={input_placeholder}, class={input_class}")
        except:
            pass
    
    # 查找所有button元素
    print("\n【查找所有button元素】")
    buttons = driver.find_elements(By.TAG_NAME, 'button')
    print(f"找到 {len(buttons)} 个button元素")
    
    for i, btn in enumerate(buttons[:5], 1):
        try:
            button_text = btn.text
            button_type = btn.get_attribute('type') or 'button'
            print(f"  {i}. text={button_text}, type={button_type}")
        except:
            pass
    
    # 查找所有form元素
    print("\n【查找所有form元素】")
    forms = driver.find_elements(By.TAG_NAME, 'form')
    print(f"找到 {len(forms)} 个form元素")
    
    for i, form in enumerate(forms[:5], 1):
        try:
            form_class = form.get_attribute('class') or 'None'
            print(f"  {i}. class={form_class}")
        except:
            pass
    
    # 检查是否有错误信息
    print("\n【检查错误信息】")
    try:
        error_messages = driver.find_elements(By.CSS_SELECTOR, '.el-message--error')
        print(f"找到 {len(error_messages)} 个错误消息")
        for msg in error_messages:
            print(f"  - {msg.text}")
    except:
        print("  未找到错误消息")
    
    # 截图
    driver.save_screenshot('diagnosis-login.png')
    print("\n已保存截图: diagnosis-login.png")
    
    # 检查控制台日志
    print("\n【检查浏览器控制台】")
    logs = driver.get_log('browser')
    if logs:
        for entry in logs:
            print(f"  {entry}")
    
    # 访问调研页面
    print("\n" + "=" * 60)
    print("【检查调研页面】")
    print("=" * 60)
    driver.get("http://localhost:3000/survey")
    time.sleep(3)
    
    # 查找表格元素
    print("\n【查找表格元素】")
    tables = driver.find_elements(By.TAG_NAME, 'table')
    print(f"找到 {len(tables)} 个table元素")
    
    el_tables = driver.find_elements(By.CSS_SELECTOR, '.el-table')
    print(f"找到 {len(el_tables)} 个.el-table元素")
    
    # 截图
    driver.save_screenshot('diagnosis-survey.png')
    print("已保存截图: diagnosis-survey.png")
    
    # 访问数据分析页面
    print("\n" + "=" * 60)
    print("【检查数据分析页面】")
    print("=" * 60)
    driver.get("http://localhost:3000/analysis")
    time.sleep(3)
    
    # 查找标签切换按钮
    print("\n【查找标签切换按钮】")
    radio_buttons = driver.find_elements(By.CSS_SELECTOR, '.el-radio-button')
    print(f"找到 {len(radio_buttons)} 个.el-radio-button元素")
    
    radio_groups = driver.find_elements(By.CSS_SELECTOR, '.el-radio-group')
    print(f"找到 {len(radio_groups)} 个.el-radio-group元素")
    
    # 截图
    driver.save_screenshot('diagnosis-analysis.png')
    print("已保存截图: diagnosis-analysis.png")
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    
except Exception as e:
    print(f"诊断出错: {str(e)}")
    import traceback
    print(traceback.format_exc())
finally:
    input("\n按回车键关闭浏览器...")
    driver.quit()
