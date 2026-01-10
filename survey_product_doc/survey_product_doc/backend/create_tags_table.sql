-- 创建标签表的SQL脚本
-- 用于添加标签功能到题库管理系统

USE survey_db;

-- 创建标签表
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(20) DEFAULT '#409EFF',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tag_name (name)
);

-- 创建题目标签关联表（多对多关系）
CREATE TABLE IF NOT EXISTS question_tags (
    question_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (question_id, tag_id),
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    INDEX idx_question_tags_question_id (question_id),
    INDEX idx_question_tags_tag_id (tag_id)
);

-- 插入一些示例标签数据
INSERT IGNORE INTO tags (name, color, description) VALUES
('员工福利', '#67C23A', '关于员工福利、薪资、保险等方面的问题'),
('工作环境', '#E6A23C', '关于工作环境、办公条件、设施等方面的问题'),
('团队协作', '#409EFF', '关于团队合作、沟通、协作等方面的问题'),
('领导力', '#F56C6C', '关于领导能力、管理风格、决策等方面的问题'),
('职业发展', '#909399', '关于职业规划、培训、晋升等方面的问题'),
('公司文化', '#9C27B0', '关于企业文化、价值观、氛围等方面的问题'),
('工作满意度', '#FF9800', '关于工作满意度、工作体验等方面的问题'),
('创新思维', '#4CAF50', '关于创新、创意、改进建议等方面的问题');

-- 为现有题目添加一些示例标签关联
-- 注意：这里需要根据实际的题目ID来调整
INSERT IGNORE INTO question_tags (question_id, tag_id) 
SELECT q.id, t.id 
FROM questions q, tags t 
WHERE t.name IN ('员工福利', '工作环境', '团队协作') 
AND q.id <= 20;  -- 假设前20个题目添加标签

-- 显示创建结果
SELECT 'Tags table created successfully' as status;
SELECT COUNT(*) as total_tags FROM tags;
SELECT COUNT(*) as total_question_tags FROM question_tags;
