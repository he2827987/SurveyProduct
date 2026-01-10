<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside width="230px" class="aside">
        <div class="logo">企业问卷调查系统</div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          background-color="#001529"
          text-color="#fff"
          active-text-color="#409EFF"
          :collapse="isCollapse"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-menu-item index="/organization">
            <el-icon><OfficeBuilding /></el-icon>
            <span>组织架构管理</span>
          </el-menu-item>
          
          <el-menu-item index="/question">
            <el-icon><Document /></el-icon>
            <span>题库管理</span>
          </el-menu-item>
          
          <el-menu-item index="/survey">
            <el-icon><Edit /></el-icon>
            <span>调研管理</span>
          </el-menu-item>
          
          <el-menu-item index="/analysis">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据分析</span>
          </el-menu-item>
          
          <el-menu-item index="/compare">
            <el-icon><PieChart /></el-icon>
            <span>企业对比</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主要内容区 -->
      <el-container class="main-container">
        <!-- 顶部栏 -->
        <el-header height="60px" class="header">
          <div class="flex-between">
            <el-icon
              class="toggle-icon"
              @click="toggleSidebar"
            >
              <component :is="isCollapse ? 'Expand' : 'Fold'" />
            </el-icon>
            
            <div class="user-info">
              <el-dropdown @command="handleCommand">
                <span class="user-dropdown">
                  {{ userInfo.username || '用户' }}
                  <el-icon><ArrowDown /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                    <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-header>
        
        <!-- 内容区 -->
        <el-main class="main-content">
          <router-view></router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

// 简化图标导入，只导入必要的图标
import { 
  House, 
  OfficeBuilding, 
  Document, 
  Edit, 
  DataAnalysis, 
  PieChart, 
  Expand, 
  Fold, 
  ArrowDown 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)
const userInfo = ref({
  username: '管理员'
})

// ===== 计算属性 =====

/**
 * 当前激活的菜单项
 */
const activeMenu = computed(() => {
  return route.path
})

// ===== 方法 =====

/**
 * 切换侧边栏折叠状态
 */
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

/**
 * 处理用户下拉菜单命令
 * @param {string} command - 命令名称
 */
const handleCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm(
          '确定要退出登录吗？',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        // 清除本地存储的token
        localStorage.removeItem('access_token')
        
        // 跳转到登录页
        router.push('/login')
        
        ElMessage.success('已退出登录')
      } catch {
        // 用户取消操作
      }
      break
  }
}
</script>

<style scoped>
/* 布局容器 */
.layout-container {
  height: 100vh;
  width: 100%;
}

/* 侧边栏样式 */
.aside {
  background-color: #001529;
  height: 100vh;
  overflow-x: hidden;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #002140;
  white-space: nowrap;
  overflow: hidden;
}

.el-menu-vertical {
  border-right: none;
}

/* 主容器 */
.main-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 顶部栏样式 */
.header {
  background-color: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.toggle-icon {
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.toggle-icon:hover {
  color: #409eff;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-dropdown {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #666;
}

.user-dropdown:hover {
  color: #409eff;
}

/* 主内容区样式 */
.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  height: calc(100vh - 60px);
  overflow-y: auto;
  flex: 1;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .aside {
    width: 64px !important;
  }
  
  .logo {
    font-size: 12px;
  }
  
  .main-content {
    padding: 10px;
  }
}
</style> 