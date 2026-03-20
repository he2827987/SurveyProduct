#!/bin/bash

# SurveyProduct 测试套件完整运行脚本

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  SurveyProduct 测试套件执行脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 解析参数
TEST_TYPE=${1:-all}
CLEANUP=${2:-false}

# 检查依赖
check_dependencies() {
    echo -e "${YELLOW}检查依赖...${NC}"
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Python3 未安装${NC}"
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}Node.js 未安装${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}依赖检查完成${NC}"
    echo ""
}

# 安装依赖
install_dependencies() {
    echo -e "${YELLOW}安装测试依赖...${NC}"
    
    # 安装Python依赖
    pip install -q pytest pytest-cov pytest-asyncio pytest-mock pytest-html pytest-xdist
    
    # 安装Node.js依赖
    cd frontend
    npm install --silent
    cd ..
    
    echo -e "${GREEN}依赖安装完成${NC}"
    echo ""
}

# 运行后端单元测试
run_backend_unit_tests() {
    echo -e "${YELLOW}运行后端单元测试...${NC}"
    pytest tests/unit/backend/ -v -m unit --tb=short
    echo -e "${GREEN}后端单元测试完成${NC}"
    echo ""
}

# 运行后端集成测试
run_backend_integration_tests() {
    echo -e "${YELLOW}运行后端集成测试...${NC}"
    pytest tests/integration/ -v -m integration --tb=short
    echo -e "${GREEN}后端集成测试完成${NC}"
    echo ""
}

# 运行后端API测试
run_api_tests() {
    echo -e "${YELLOW}运行API集成测试...${NC}"
    pytest tests/integration/api/ -v -m api --tb=short
    echo -e "${GREEN}API集成测试完成${NC}"
    echo ""
}

# 运行安全测试
run_security_tests() {
    echo -e "${YELLOW}运行安全测试...${NC}"
    pytest tests/security/ -v -m security --tb=short
    echo -e "${GREEN}安全测试完成${NC}"
    echo ""
}

# 运行前端测试
run_frontend_tests() {
    echo -e "${YELLOW}运行前端测试...${NC}"
    cd frontend
    npm run test -- --run
    cd ..
    echo -e "${GREEN}前端测试完成${NC}"
    echo ""
}

# 运行E2E测试
run_e2e_tests() {
    echo -e "${YELLOW}运行E2E测试...${NC}"
    npm run test:desktop
    echo -e "${GREEN}E2E测试完成${NC}"
    echo ""
}

# 生成覆盖率报告
generate_coverage_report() {
    echo -e "${YELLOW}生成覆盖率报告...${NC}"
    pytest tests/ --cov=backend --cov-report=html --cov-report=term
    echo -e "${GREEN}覆盖率报告已生成: htmlcov/index.html${NC}"
    echo ""
}

# 清理测试数据
cleanup() {
    if [ "$CLEANUP" = true ]; then
        echo -e "${YELLOW}清理测试数据...${NC}"
        rm -rf htmlcov/
        rm -rf .pytest_cache/
        rm -rf test-results/
        rm -rf coverage/
        echo -e "${GREEN}清理完成${NC}"
        echo ""
    fi
}

# 主函数
main() {
    # 检查依赖
    check_dependencies
    
    # 清理
    cleanup
    
    case $TEST_TYPE in
        unit)
            install_dependencies
            run_backend_unit_tests
            ;;
        integration)
            install_dependencies
            run_backend_integration_tests
            ;;
        api)
            install_dependencies
            run_api_tests
            ;;
        security)
            install_dependencies
            run_security_tests
            ;;
        frontend)
            run_frontend_tests
            ;;
        e2e)
            run_e2e_tests
            ;;
        coverage)
            install_dependencies
            generate_coverage_report
            ;;
        all)
            install_dependencies
            run_backend_unit_tests
            run_backend_integration_tests
            run_api_tests
            run_security_tests
            run_frontend_tests
            # E2E测试需要单独运行，因为它需要完整的应用环境
            echo -e "${YELLOW}E2E测试请单独运行: ./run_tests.sh e2e${NC}"
            generate_coverage_report
            ;;
        *)
            echo -e "${RED}未知测试类型: $TEST_TYPE${NC}"
            echo "用法: ./run_tests.sh [unit|integration|api|security|frontend|e2e|coverage|all] [cleanup]"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  测试执行完成${NC}"
    echo -e "${GREEN}========================================${NC}"
}

# 运行主函数
main
