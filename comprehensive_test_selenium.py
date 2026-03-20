#!/usr/bin/env python3
"""
全面功能测试 - 使用Selenium进行浏览器自动化测试
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
from datetime import datetime

# 测试配置
CONFIG = {
    'base_url': 'http://localhost:3000',
    'email': 'he282987@gmail.com',
    'password': '12345678',
    'timeout': 10
}

# 测试结果
test_results = {
    'passed': [],
    'failed': [],
    'errors': [],
    'start_time': None,
    'end_time': None
}

def log(message, level='INFO'):
    """日志函数"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    prefix = {
        'INFO': 'ℹ️',
        'SUCCESS': '✅',
        'ERROR': '❌',
        'WARNING': '⚠️'
    }.get(level, 'ℹ️')
    print(f"{prefix} [{timestamp}] {message}")

def wait_seconds(seconds):
    """等待函数"""
    time.sleep(seconds)

def save_test_results():
    """保存测试结果"""
    test_results['end_time'] = datetime.now().isoformat()
    
    with open('test-report-selenium.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    log('测试报告已保存到 test-report-selenium.json')

def main():
    log('=' * 50)
    log('开始全面功能测试')
    log('=' * 50)
    
    test_results['start_time'] = datetime.now().isoformat()
    
    # 初始化浏览器
    log('初始化浏览器...')
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1280,720')
    # options.add_argument('--headless')  # 无头模式，取消注释可以不显示浏览器窗口
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait_driver = WebDriverWait(driver, CONFIG['timeout'])
    
    try:
        # ==================== 第一阶段：认证功能 ====================
        log('\n【第一阶段：认证功能测试】')
        
        # 测试1.1: 访问登录页面
        log('测试 1.1: 访问登录页面')
        driver.get(f"{CONFIG['base_url']}/login")
        wait_seconds(2)
        
        try:
            login_form = wait_driver.until(EC.presence_of_element_located((By.TAG_NAME, 'form')))
            log('登录表单可见', 'SUCCESS')
            test_results['passed'].append('1.1 登录表单显示')
        except TimeoutException:
            log('登录表单不可见', 'ERROR')
            test_results['failed'].append('1.1 登录表单显示')
            driver.save_screenshot('test-screenshots/login-form-error.png')
        
        # 测试1.2: 填写登录信息
        log('测试 1.2: 填写登录信息')
        try:
            # 尝试多种方式找到邮箱输入框
            email_input = None
            try:
                email_input = driver.find_element(By.CSS_SELECTOR, 'input[type="email"]')
            except NoSuchElementException:
                try:
                    email_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="邮箱"]')
                except NoSuchElementException:
                    email_input = driver.find_element(By.CSS_SELECTOR, 'input[placeholder*="Email"]')
            
            # 找到密码输入框
            password_input = driver.find_element(By.CSS_SELECTOR, 'input[type="password"]')
            
            email_input.clear()
            email_input.send_keys(CONFIG['email'])
            password_input.clear()
            password_input.send_keys(CONFIG['password'])
            
            log('登录信息填写成功', 'SUCCESS')
            test_results['passed'].append('1.2 填写登录信息')
        except Exception as e:
            log(f'填写登录信息失败: {str(e)}', 'ERROR')
            test_results['failed'].append('1.2 填写登录信息')
            driver.save_screenshot('test-screenshots/login-input-error.png')
        
        # 测试1.3: 点击登录按钮
        log('测试 1.3: 点击登录按钮')
        try:
            login_button = None
            try:
                login_button = driver.find_element(By.XPATH, '//button[contains(text(), "登录")]')
            except NoSuchElementException:
                login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            
            login_button.click()
            log('登录按钮点击成功', 'SUCCESS')
            
            # 等待跳转
            wait_seconds(3)
            
            current_url = driver.current_url
            log(f'当前URL: {current_url}')
            
            if '/login' not in current_url:
                log('登录后成功跳转', 'SUCCESS')
                test_results['passed'].append('1.3 登录跳转')
            else:
                log('登录后未跳转', 'ERROR')
                test_results['failed'].append('1.3 登录跳转')
                
                # 检查是否有错误提示
                try:
                    error_message = driver.find_element(By.CSS_SELECTOR, '.el-message--error')
                    log(f'登录错误: {error_message.text}', 'ERROR')
                except NoSuchElementException:
                    pass
                
                driver.save_screenshot('test-screenshots/login-error.png')
        except Exception as e:
            log(f'点击登录按钮失败: {str(e)}', 'ERROR')
            test_results['failed'].append('1.3 点击登录按钮')
        
        # ==================== 第二阶段：调研管理 ====================
        log('\n【第二阶段：调研管理测试】')
        
        # 测试2.1: 访问调研列表页面
        log('测试 2.1: 访问调研列表页面')
        driver.get(f"{CONFIG['base_url']}/survey")
        wait_seconds(3)
        
        # 测试2.2: 检查调研列表显示
        log('测试 2.2: 检查调研列表显示')
        try:
            # 等待表格加载
            table = wait_driver.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.el-table')))
            log('调研列表表格已加载', 'SUCCESS')
            test_results['passed'].append('2.2 调研列表显示')
        except TimeoutException:
            log('调研列表表格未显示', 'ERROR')
            test_results['failed'].append('2.2 调研列表显示')
            driver.save_screenshot('test-screenshots/survey-list-error.png')
        
        # 测试2.3: 测试创建调研按钮
        log('测试 2.3: 测试创建调研功能')
        try:
            create_button = driver.find_element(By.XPATH, '//button[contains(text(), "创建") or contains(text(), "新建")]')
            create_button.click()
            wait_seconds(1)
            
            # 检查对话框是否打开
            dialog = wait_driver.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.el-dialog')))
            log('创建调研对话框打开成功', 'SUCCESS')
            test_results['passed'].append('2.3 创建调研对话框')
            
            # 关闭对话框
            try:
                close_button = driver.find_element(By.CSS_SELECTOR, '.el-dialog__close')
                close_button.click()
                wait_seconds(0.5)
            except NoSuchElementException:
                pass
        except Exception as e:
            log(f'创建调研对话框未打开: {str(e)}', 'WARNING')
        
        # ==================== 第三阶段：题库管理 ====================
        log('\n【第三阶段：题库管理测试】')
        
        log('测试 3.1: 访问题库页面')
        driver.get(f"{CONFIG['base_url']}/question")
        wait_seconds(3)
        
        log('测试 3.2: 检查题目列表显示')
        try:
            question_list = wait_driver.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.el-table')))
            log('题库列表显示正常', 'SUCCESS')
            test_results['passed'].append('3.2 题库列表显示')
        except TimeoutException:
            log('题库列表未显示', 'ERROR')
            test_results['failed'].append('3.2 题库列表显示')
            driver.save_screenshot('test-screenshots/question-list-error.png')
        
        # ==================== 第四阶段：数据分析 ====================
        log('\n【第四阶段：数据分析测试】')
        
        log('测试 4.1: 访问数据分析页面')
        driver.get(f"{CONFIG['base_url']}/analysis")
        wait_seconds(3)
        
        log('测试 4.2: 检查标签切换按钮')
        try:
            tab_buttons = driver.find_elements(By.CSS_SELECTOR, '.el-radio-button')
            
            if len(tab_buttons) >= 3:
                log(f'找到 {len(tab_buttons)} 个标签切换按钮', 'SUCCESS')
                test_results['passed'].append('4.2 标签切换按钮显示')
                
                # 测试切换功能
                log('测试 4.3: 测试标签切换功能')
                for i in range(min(3, len(tab_buttons))):
                    tab_buttons[i].click()
                    wait_seconds(1)
                log('标签切换功能正常', 'SUCCESS')
                test_results['passed'].append('4.3 标签切换功能')
            else:
                log(f'标签切换按钮数量不正确: {len(tab_buttons)}', 'ERROR')
                test_results['failed'].append('4.2 标签切换按钮显示')
                driver.save_screenshot('test-screenshots/analysis-tabs-error.png')
        except Exception as e:
            log(f'标签切换按钮检查失败: {str(e)}', 'ERROR')
            test_results['failed'].append('4.2 标签切换按钮显示')
        
        # ==================== 第五阶段：页面导航 ====================
        log('\n【第五阶段：页面导航测试】')
        
        nav_items = [
            {'name': '仪表板', 'path': '/dashboard'},
            {'name': '调研管理', 'path': '/survey'},
            {'name': '题库管理', 'path': '/question'},
            {'name': '数据分析', 'path': '/analysis'}
        ]
        
        for item in nav_items:
            log(f'测试导航: {item["name"]}')
            driver.get(f"{CONFIG['base_url']}{item['path']}")
            wait_seconds(2)
            
            current_url = driver.current_url
            if item['path'] in current_url:
                log(f'{item["name"]} 页面加载成功', 'SUCCESS')
                test_results['passed'].append(f'导航-{item["name"]}')
            else:
                log(f'{item["name"]} 页面加载失败', 'ERROR')
                test_results['failed'].append(f'导航-{item["name"]}')
        
        # ==================== 测试结果汇总 ====================
        log('\n' + '=' * 50)
        log('测试结果汇总')
        log('=' * 50)
        
        log(f'\n✅ 通过的测试 ({len(test_results["passed"])}):')
        for index, test in enumerate(test_results['passed'], 1):
            log(f'  {index}. {test}', 'SUCCESS')
        
        log(f'\n❌ 失败的测试 ({len(test_results["failed"])}):')
        for index, test in enumerate(test_results['failed'], 1):
            log(f'  {index}. {test}', 'ERROR')
        
        if test_results['errors']:
            log(f'\n⚠️ 错误 ({len(test_results["errors"])}):')
            for index, error in enumerate(test_results['errors'], 1):
                log(f'  {index}. {error}', 'ERROR')
        
        total = len(test_results['passed']) + len(test_results['failed'])
        pass_rate = round(len(test_results['passed']) / total * 100) if total > 0 else 0
        
        log(f'\n总计: {total} 个测试')
        log(f'通过率: {pass_rate}%')
        
        # 保存测试报告
        save_test_results()
        
    except Exception as e:
        log(f'测试执行出错: {str(e)}', 'ERROR')
        import traceback
        log(traceback.format_exc(), 'ERROR')
        driver.save_screenshot('test-screenshots/error.png')
    finally:
        driver.quit()
        log('\n浏览器已关闭')

if __name__ == '__main__':
    main()
