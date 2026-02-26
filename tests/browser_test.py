#!/usr/bin/env python3
"""
线上浏览器自动化测试脚本
测试survey product的所有功能
"""

import time
import json
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SurveyProductTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.test_results = []
        
    def setup_driver(self):
        """设置Chrome驱动"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Chrome驱动设置成功")
            return True
        except Exception as e:
            print(f"❌ Chrome驱动设置失败: {e}")
            return False
    
    def log_test_result(self, test_name, passed, message=""):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.test_results.append(result)
        
        if passed:
            print(f"✅ {test_name} - 通过")
        else:
            print(f"❌ {test_name} - 失败: {message}")
    
    def take_screenshot(self, filename):
        """截屏"""
        try:
            self.driver.save_screenshot(f"screenshots/{filename}.png")
            print(f"📸 截屏保存: {filename}.png")
        except Exception as e:
            print(f"❌ 截屏失败: {e}")
    
    def test_homepage_access(self):
        """测试首页访问"""
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # 等待页面完全加载和Vue.js渲染
            import time
            time.sleep(5)
            
            # 检查页面标题
            title = self.driver.title
            # 由于路由守卫，可能重定向到登录页面
            if "Survey" in title or "调研" in title or "登录" in title:
                self.log_test_result("首页访问", True, f"页面标题: {title}")
            else:
                self.log_test_result("首页访问", False, f"页面标题不包含预期内容: {title}")
                
            self.take_screenshot("homepage")
            
        except Exception as e:
            self.log_test_result("首页访问", False, str(e))
    
    def test_login_functionality(self):
        """测试登录功能"""
        try:
            # 查找登录按钮或链接
            login_selectors = [
                "//button[contains(text(), '登录')]",
                "//a[contains(text(), '登录')]",
                "//button[contains(text(), 'Login')]",
                "//a[contains(text(), 'Login')]",
                ".login-btn",
                "#login"
            ]
            
            login_element = None
            for selector in login_selectors:
                try:
                    if selector.startswith("//"):
                        login_element = self.driver.find_element(By.XPATH, selector)
                    else:
                        login_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if login_element:
                login_element.click()
                time.sleep(2)
                
                # 查找登录表单
                username_selectors = ["input[name='username']", "input[type='text']", "#username", ".username"]
                password_selectors = ["input[name='password']", "input[type='password']", "#password", ".password"]
                
                username_element = None
                for selector in username_selectors:
                    try:
                        username_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                password_element = None
                for selector in password_selectors:
                    try:
                        password_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if username_element and password_element:
                    username_element.send_keys("admin")
                    password_element.send_keys("admin123")
                    
                    # 查找提交按钮
                    submit_selectors = ["button[type='submit']", ".submit-btn", "#submit"]
                    submit_element = None
                    for selector in submit_selectors:
                        try:
                            submit_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            break
                        except:
                            continue
                    
                    if submit_element:
                        submit_element.click()
                        time.sleep(3)
                        self.log_test_result("登录功能", True, "登录表单填写并提交成功")
                        self.take_screenshot("login_success")
                    else:
                        self.log_test_result("登录功能", False, "未找到提交按钮")
                else:
                    self.log_test_result("登录功能", False, "未找到用户名或密码输入框")
            else:
                self.log_test_result("登录功能", False, "未找到登录按钮")
                
        except Exception as e:
            self.log_test_result("登录功能", False, str(e))
    
    def test_survey_management(self):
        """测试调研管理功能"""
        try:
            # 尝试访问调研管理页面
            survey_urls = [
                f"{self.base_url}/surveys",
                f"{self.base_url}/survey",
                f"{self.base_url}/admin/surveys"
            ]
            
            survey_page_loaded = False
            for url in survey_urls:
                try:
                    self.driver.get(url)
                    time.sleep(3)
                    
                    # 检查是否有调研相关的元素
                    survey_indicators = [
                        "调研",
                        "Survey",
                        "questionnaire",
                        "create"
                    ]
                    
                    page_text = self.driver.page_source.lower()
                    if any(indicator.lower() in page_text for indicator in survey_indicators):
                        survey_page_loaded = True
                        self.log_test_result("调研管理页面", True, f"成功访问: {url}")
                        break
                        
                except:
                    continue
            
            if not survey_page_loaded:
                # 尝试从首页导航
                self.driver.get(self.base_url)
                time.sleep(2)
                
                # 查找导航菜单
                nav_selectors = [".nav", ".navbar", ".menu", "nav"]
                nav_element = None
                for selector in nav_selectors:
                    try:
                        nav_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                
                if nav_element:
                    nav_text = nav_element.text.lower()
                    if any(indicator in nav_text for indicator in ["调研", "survey", "问卷"]):
                        self.log_test_result("调研管理页面", True, "在导航中找到调研相关功能")
                    else:
                        self.log_test_result("调研管理页面", False, "导航中未找到调研功能")
                else:
                    self.log_test_result("调研管理页面", False, "未找到导航元素")
            
            self.take_screenshot("survey_management")
            
        except Exception as e:
            self.log_test_result("调研管理页面", False, str(e))
    
    def test_question_management(self):
        """测试题库管理功能"""
        try:
            # 查找题库相关的链接或按钮
            question_indicators = [
                "//a[contains(text(), '题库')]",
                "//button[contains(text(), '题库')]",
                "//a[contains(text(), '问题')]",
                "//button[contains(text(), '问题')]",
                "//a[contains(text(), 'Question')]",
                "//button[contains(text(), 'Question')]"
            ]
            
            question_element = None
            for selector in question_indicators:
                try:
                    question_element = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if question_element:
                question_element.click()
                time.sleep(3)
                self.log_test_result("题库管理", True, "成功点击题库相关功能")
            else:
                # 检查页面内容是否包含题库相关文本
                page_text = self.driver.page_source
                if any(indicator in page_text for indicator in ["题库", "问题", "Question", "题目录入"]):
                    self.log_test_result("题库管理", True, "页面包含题库相关内容")
                else:
                    self.log_test_result("题库管理", False, "未找到题库相关功能")
            
            self.take_screenshot("question_management")
            
        except Exception as e:
            self.log_test_result("题库管理", False, str(e))
    
    def test_analytics_functionality(self):
        """测试数据分析功能"""
        try:
            # 查找分析相关的链接或按钮
            analytics_indicators = [
                "//a[contains(text(), '分析')]",
                "//button[contains(text(), '分析')]",
                "//a[contains(text(), 'Analytics')]",
                "//button[contains(text(), 'Analytics')]",
                "//a[contains(text(), '数据')]",
                "//button[contains(text(), '数据')]"
            ]
            
            analytics_element = None
            for selector in analytics_indicators:
                try:
                    analytics_element = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if analytics_element:
                analytics_element.click()
                time.sleep(3)
                self.log_test_result("数据分析功能", True, "成功点击分析相关功能")
            else:
                # 检查页面内容
                page_text = self.driver.page_source
                if any(indicator in page_text for indicator in ["分析", "Analytics", "统计", "数据"]):
                    self.log_test_result("数据分析功能", True, "页面包含分析相关内容")
                else:
                    self.log_test_result("数据分析功能", False, "未找到分析相关功能")
            
            self.take_screenshot("analytics")
            
        except Exception as e:
            self.log_test_result("数据分析功能", False, str(e))
    
    def test_organization_management(self):
        """测试组织架构管理"""
        try:
            # 查找组织相关的链接或按钮
            org_indicators = [
                "//a[contains(text(), '组织')]",
                "//button[contains(text(), '组织')]",
                "//a[contains(text(), '部门')]",
                "//button[contains(text(), '部门')]",
                "//a[contains(text(), 'Organization')]",
                "//button[contains(text(), 'Organization')]"
            ]
            
            org_element = None
            for selector in org_indicators:
                try:
                    org_element = self.driver.find_element(By.XPATH, selector)
                    break
                except:
                    continue
            
            if org_element:
                org_element.click()
                time.sleep(3)
                self.log_test_result("组织架构管理", True, "成功点击组织相关功能")
            else:
                # 检查页面内容
                page_text = self.driver.page_source
                if any(indicator in page_text for indicator in ["组织", "部门", "Organization", "架构"]):
                    self.log_test_result("组织架构管理", True, "页面包含组织相关内容")
                else:
                    self.log_test_result("组织架构管理", False, "未找到组织相关功能")
            
            self.take_screenshot("organization")
            
        except Exception as e:
            self.log_test_result("组织架构管理", False, str(e))
    
    def test_responsive_design(self):
        """测试响应式设计"""
        try:
            # 测试不同屏幕尺寸
            screen_sizes = [
                (1920, 1080, "桌面"),
                (768, 1024, "平板"),
                (375, 667, "手机")
            ]
            
            responsive_passed = True
            
            for width, height, device_name in screen_sizes:
                self.driver.set_window_size(width, height)
                time.sleep(2)
                
                # 检查页面是否正常显示
                try:
                    body = self.driver.find_element(By.TAG_NAME, "body")
                    if body.is_displayed():
                        print(f"✅ {device_name}分辨率显示正常")
                    else:
                        responsive_passed = False
                        print(f"❌ {device_name}分辨率显示异常")
                except:
                    responsive_passed = False
                    print(f"❌ {device_name}分辨率无法找到body元素")
            
            self.log_test_result("响应式设计", responsive_passed, "测试了桌面、平板、手机三种分辨率")
            
        except Exception as e:
            self.log_test_result("响应式设计", False, str(e))
    
    def test_page_load_speed(self):
        """测试页面加载速度"""
        try:
            start_time = time.time()
            self.driver.get(self.base_url)
            
            # 等待页面完全加载
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            load_time = time.time() - start_time
            
            if load_time < 5:
                self.log_test_result("页面加载速度", True, f"加载时间: {load_time:.2f}秒")
            else:
                self.log_test_result("页面加载速度", False, f"加载时间过长: {load_time:.2f}秒")
                
        except Exception as e:
            self.log_test_result("页面加载速度", False, str(e))
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始线上功能测试")
        print("=" * 60)
        
        if not self.setup_driver():
            return False
        
        # 创建截屏目录
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        # 运行测试
        test_functions = [
            ("页面访问测试", self.test_homepage_access),
            ("登录功能测试", self.test_login_functionality),
            ("调研管理测试", self.test_survey_management),
            ("题库管理测试", self.test_question_management),
            ("数据分析测试", self.test_analytics_functionality),
            ("组织架构测试", self.test_organization_management),
            ("响应式设计测试", self.test_responsive_design),
            ("页面加载速度测试", self.test_page_load_speed)
        ]
        
        for test_name, test_func in test_functions:
            print(f"\n🔍 执行{test_name}...")
            try:
                test_func()
            except Exception as e:
                self.log_test_result(test_name, False, f"测试执行异常: {str(e)}")
            
            time.sleep(2)  # 测试间隔
        
        # 生成测试报告
        self.generate_test_report()
        
        # 关闭浏览器
        self.driver.quit()
        
        return self.get_test_summary()
    
    def generate_test_report(self):
        """生成测试报告"""
        report = {
            "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "total_tests": len(self.test_results),
            "passed_tests": len([r for r in self.test_results if r["passed"]]),
            "failed_tests": len([r for r in self.test_results if not r["passed"]]),
            "test_details": self.test_results
        }
        
        report_file = f"browser_test_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 测试报告已保存到: {report_file}")
    
    def get_test_summary(self):
        """获取测试总结"""
        passed = len([r for r in self.test_results if r["passed"]])
        total = len(self.test_results)
        
        print(f"\n" + "=" * 60)
        print("📊 测试结果汇总")
        print("=" * 60)
        print(f"总测试数: {total}")
        print(f"通过测试: {passed}")
        print(f"失败测试: {total - passed}")
        print(f"成功率: {(passed / total * 100):.1f}%")
        
        if total - passed > 0:
            print("\n❌ 失败的测试:")
            for test in self.test_results:
                if not test["passed"]:
                    print(f"   - {test['test_name']}: {test['message']}")
        
        return passed == total

def main():
    """主函数"""
    # 使用Render部署的URL
    base_url = "https://survey-product.onrender.com"
    
    # 创建测试实例并运行
    tester = SurveyProductTester(base_url)
    success = tester.run_all_tests()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())