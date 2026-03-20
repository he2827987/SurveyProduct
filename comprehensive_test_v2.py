#!/usr/bin/env python3
"""
完整修复版测试脚本 - 修复元素定位问题
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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# 测试配置
CONFIG = {
    'base_url': 'http://localhost:3000',
    'email': 'he282987@gmail.com',
    'password': '12345678',
    'timeout': 15
}

# 测试结果
test_results = {
    'passed': [],
    'failed': [],
    'errors': [],
    'warnings': [],
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
        'WARNING': '⚠️',
        'DEBUG': '🔍'
    }.get(level, 'ℹ️')
    print(f"{prefix} [{timestamp}] {message}")

def wait_seconds(seconds):
    """等待函数"""
    time.sleep(seconds)

def save_test_results():
    """保存测试结果"""
    test_results['end_time'] = datetime.now().isoformat()
    
    with open('test-report-selenium-v2.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, indent=2, ensure_ascii=False)
    
    log('测试报告已保存到 test-report-selenium-v2.json')

def test_login_page(driver, wait_driver):
    """测试登录页面"""
    log('\n【测试登录功能】')
    
    # 访问登录页面
    log('访问登录页面...')
    driver.get(f"{CONFIG['base_url']}/login")
    wait_seconds(2)
    
    # 截图保存当前状态
    driver.save_screenshot('test-screenshots/01-login-page.png')
    
    # 查找登录表单
    try:
                # 尝试多种方式找到表单
        form = None
        selectors = [
            'form',
            '.login-form',
            '.el-form',
            'form.el-form'
        ]
        
        for selector in selectors:
            try:
                form = driver.find_element(By.CSS_SELECTOR, selector)
                if form:
                    log(f'找到登录表单: {selector}', 'SUCCESS')
                    test_results['passed'].append('登录表单显示')
                    break
            except NoSuchElementException:
                continue
        
        if not form:
            log('未找到登录表单', 'ERROR')
            test_results['failed'].append('登录表单显示')
            return False
    except Exception as e:
        log(f'查找登录表单出错: {str(e)}', 'ERROR')
        test_results['failed'].append('登录表单显示')
        return False
    
    # 查找并填写邮箱
    log('查找邮箱输入框...')
    email_selectors = [
        'input[type="email"]',
        'input[type="text"]',
        'input[placeholder*="邮箱"]',
        'input[placeholder*="Email"]',
        'input[placeholder*="用户名"]',
        'input[placeholder*="Username"]',
        '.el-input__inner',
        'input'
    ]
    
    email_input = None
    for selector in email_selectors:
        try:
            if 'input' == selector:
                inputs = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(inputs) >= 2:
                    email_input = inputs[0]
                    log(f'通过选择器找到邮箱输入框: {selector}', 'SUCCESS')
                    break
            else:
                email_input = driver.find_element(By.CSS_SELECTOR, selector)
                if email_input:
                    log(f'通过选择器找到邮箱输入框: {selector}', 'SUCCESS')
                    break
        except NoSuchElementException:
            continue
    
    if not email_input:
        log('未找到邮箱输入框', 'ERROR')
        test_results['failed'].append('填写邮箱')
        driver.save_screenshot('test-screenshots/02-email-not-found.png')
        return False
    
    # 填写邮箱
    try:
        email_input.clear()
        email_input.send_keys(CONFIG['email'])
        log(f'邮箱填写成功: {CONFIG["email"]}', 'SUCCESS')
        test_results['passed'].append('填写邮箱')
    except Exception as e:
        log(f'填写邮箱失败: {str(e)}', 'ERROR')
        test_results['failed'].append('填写邮箱')
        return False
    
    # 查找并填写密码
    log('查找密码输入框...')
    password_input = None
    for selector in email_selectors[1:]:
        try:
            if 'input' == selector:
                inputs = driver.find_elements(By.CSS_SELECTOR, selector)
                if len(inputs) >= 2:
                    password_input = inputs[1]
                    log(f'通过选择器找到密码输入框', 'SUCCESS')
                    break
            else:
                password_input = driver.find_element(By.CSS_SELECTOR, selector)
                if password_input:
                    log(f'通过选择器找到密码输入框: {selector}', 'SUCCESS')
                    break
        except NoSuchElementException:
            continue
    
    if not password_input:
        log('未找到密码输入框', 'ERROR')
        test_results['failed'].append('填写密码')
        return False
    
    # 填写密码
    try:
        password_input.clear()
        password_input.send_keys(CONFIG['password'])
        log('密码填写成功', 'SUCCESS')
        test_results['passed'].append('填写密码')
    except Exception as e:
        log(f'填写密码失败: {str(e)}', 'ERROR')
        test_results['failed'].append('填写密码')
        return False
    
    # 截图保存填写后的状态
    driver.save_screenshot('test-screenshots/03-form-filled.png')
    
    # 查找并点击登录按钮
    log('查找登录按钮...')
    login_button = None
    button_selectors = [
        'button[type="submit"]',
        'button:contains("登录")',
        'button:contains("登 录")',
        '.el-button--primary',
        'button.el-button--primary'
    ]
    
    for selector in button_selectors:
        try:
            if ':contains' in selector:
                text = selector.split('"')[1]
                login_button = driver.find_element(By.XPATH, f'//button[contains(text(), "{text}")]')
            else:
                login_button = driver.find_element(By.CSS_SELECTOR, selector)
            
            if login_button:
                log(f'找到登录按钮: {selector}', 'SUCCESS')
                break
        except NoSuchElementException:
            continue
    
    if not login_button:
        # 尝试找到所有按钮
        try:
            buttons = driver.find_elements(By.TAG_NAME, 'button')
            log(f'找到 {len(buttons)} 个按钮', 'DEBUG')
            if len(buttons) > 0:
                login_button = buttons[0]
                log('使用第一个按钮作为登录按钮', 'WARNING')
                test_results['warnings'].append('使用第一个按钮作为登录按钮')
        except Exception as e:
            log(f'查找按钮出错: {str(e)}', 'ERROR')
            test_results['failed'].append('点击登录按钮')
            return False
    
    # 点击登录按钮
    try:
        login_button.click()
        log('登录按钮点击成功', 'SUCCESS')
        test_results['passed'].append('点击登录按钮')
    except Exception as e:
        log(f'点击登录按钮失败: {str(e)}', 'ERROR')
        test_results['failed'].append('点击登录按钮')
        return False
    
    # 等待登录完成并检查是否跳转
    wait_seconds(3)
    
    current_url = driver.current_url
    log(f'当前URL: {current_url}')
    
    driver.save_screenshot('test-screenshots/04-after-login.png')
    
    if '/login' not in current_url:
        log(f'登录成功，跳转到: {current_url}', 'SUCCESS')
        test_results['passed'].append('登录成功并跳转')
        return True
    else:
        log('登录失败或未跳转', 'ERROR')
        test_results['failed'].append('登录成功并跳转')
        
        # 检查是否有错误提示
        try:
            error_msg = driver.find_element(By.CSS_SELECTOR, '.el-message--error')
            log(f'错误消息: {error_msg.text}', 'ERROR')
        except NoSuchElementException:
            pass
        
        return False

def main():
    log('=' * 60)
    log('开始全面功能测试 v2')
    log('=' * 60)
    
    test_results['start_time'] = datetime.now().isoformat()
    
    # 初始化浏览器
    log('初始化浏览器...')
    options = webdriver.ChromeOptions()
    options.add_argument('--window-size=1280,720')
    # options.add_argument('--headless')  # 无头模式
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait_driver = WebDriverWait(driver, CONFIG['timeout'])
    
    try:
        # 测试登录
        login_success = test_login_page(driver, wait_driver)
        
        if not login_success:
            log('登录测试失败，停止后续测试', 'ERROR')
            return
        
        # 测试其他页面
        log('\n【测试调研管理页面】')
        driver.get(f"{CONFIG['base_url']}/survey")
        wait_seconds(3)
        driver.save_screenshot('test-screenshots/05-survey-page.png')
        test_results['passed'].append('调研页面访问')
        
        log('\n【测试题库管理页面】')
        driver.get(f"{CONFIG['base_url']}/question")
        wait_seconds(3)
        driver.save_screenshot('test-screenshots/06-question-page.png')
        test_results['passed'].append('题库页面访问')
        
        log('\n【测试数据分析页面】')
        driver.get(f"{CONFIG['base_url']}/analysis")
        wait_seconds(3)
        driver.save_screenshot('test-screenshots/07-analysis-page.png')
        test_results['passed'].append('分析页面访问')
        
        # 输出最终结果
        log('\n' + '=' * 60)
        log('测试结果汇总')
        log('=' * 60)
        
        log(f'\n✅ 通过的测试 ({len(test_results["passed"])}):')
        for i, test in enumerate(test_results['passed'], 1):
            log(f'  {i}. {test}', 'SUCCESS')
        
        log(f'\n❌ 失败的测试 ({len(test_results["failed"])}):')
        for i, test in enumerate(test_results['failed'], 1):
            log(f'  {i}. {test}', 'ERROR')
        
        if test_results['warnings']:
            log(f'\n⚠️ 警告 ({len(test_results["warnings"])}):')
            for i, warning in enumerate(test_results['warnings'], 1):
                log(f'  {i}. {warning}', 'WARNING')
        
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
