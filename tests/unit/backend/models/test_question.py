"""
题目模型单元测试
"""
import pytest
import json
from backend.app.models import Question


class TestQuestionModel:
    """题目模型测试"""

    def test_create_single_choice_question(self):
        """测试创建单选题"""
        options = ["选项A", "选项B", "选项C"]
        question = Question(
            text="这是一个单选题吗？",
            type="single_choice",
            options=json.dumps(options),
            is_required=True
        )
        assert question.type == "single_choice"
        assert question.is_required is True
        assert json.loads(question.options) == options

    def test_create_multi_choice_question(self):
        """测试创建多选题"""
        options = ["选项1", "选项2", "选项3", "选项4"]
        question = Question(
            text="请选择所有适用项",
            type="multi_choice",
            options=json.dumps(options),
            is_required=True
        )
        assert question.type == "multi_choice"
        assert len(json.loads(question.options)) == 4

    def test_create_text_input_question(self):
        """测试创建文本输入题"""
        question = Question(
            text="请输入您的意见",
            type="text_input",
            is_required=False
        )
        assert question.type == "text_input"
        assert question.is_required is False

    def test_create_number_input_question(self):
        """测试创建数字输入题"""
        question = Question(
            text="请输入您的年龄",
            type="number_input",
            is_required=True,
            min_score=0,
            max_score=100
        )
        assert question.type == "number_input"
        assert question.min_score == 0
        assert question.max_score == 100

    def test_create_sort_order_question(self):
        """测试创建排序题"""
        options = ["优先级1", "优先级2", "优先级3"]
        question = Question(
            text="请按优先级排序",
            type="sort_order",
            options=json.dumps(options),
            is_required=True
        )
        assert question.type == "sort_order"

    def test_create_conditional_question(self):
        """测试创建关联题"""
        question = Question(
            text="请说明原因",
            type="conditional",
            parent_question_id=1,
            trigger_options=json.dumps(["不满意", "非常不满意"]),
            is_required=True
        )
        assert question.type == "conditional"
        assert question.parent_question_id == 1
        assert "不满意" in json.loads(question.trigger_options)

    def test_question_default_values(self):
        """测试题目默认值"""
        question = Question(
            text="测试题目",
            type="text_input",
            owner_id=1
        )
        assert question.is_required is False
        assert question.order == 0
        assert question.usage_count == 0
        assert question.min_score == 0
        assert question.max_score == 10

    def test_question_order(self):
        """测试题目排序"""
        question1 = Question(
            text="题目1",
            type="text_input",
            order=1,
            owner_id=1
        )
        question2 = Question(
            text="题目2",
            type="text_input",
            order=2,
            owner_id=1
        )
        
        assert question1.order < question2.order

    def test_question_score_range(self):
        """测试题目分值范围"""
        question = Question(
            text="评分题目",
            type="single_choice",
            min_score=1,
            max_score=5,
            owner_id=1
        )
        assert question.min_score <= question.max_score

    def test_question_usage_count_increment(self, db_session):
        """测试题目使用次数增加"""
        question = Question(
            text="测试题目",
            type="text_input",
            usage_count=0,
            owner_id=1
        )
        db_session.add(question)
        db_session.commit()
        
        question.usage_count += 1
        db_session.commit()
        db_session.refresh(question)
        
        assert question.usage_count == 1

    def test_question_category_relationship(self, db_session):
        """测试题目分类关系"""
        from backend.app.models import Category
        
        category = Category(
            name="满意度调查",
            description="满意度相关题目"
        )
        
        question = Question(
            text="测试题目",
            type="text_input",
            category_id=category.id,
            owner_id=1
        )
        
        db_session.add(category)
        db_session.add(question)
        db_session.commit()
        
        assert question.category_id == category.id

    def test_question_organization_scope(self):
        """测试题目组织范围"""
        # 全局题目
        global_question = Question(
            text="全局题目",
            type="text_input",
            owner_id=1,
            organization_id=None
        )
        assert global_question.organization_id is None
        
        # 组织题目
        org_question = Question(
            text="组织题目",
            type="text_input",
            owner_id=1,
            organization_id=1
        )
        assert org_question.organization_id == 1

    def test_question_owner_relationship(self):
        """测试题目所有者关系"""
        question = Question(
            text="测试题目",
            type="text_input",
            owner_id=1
        )
        assert question.owner_id == 1

    def test_question_options_validation(self):
        """测试题目选项验证"""
        options = ["选项A", "选项B", "选项C"]
        question = Question(
            text="选择题",
            type="single_choice",
            options=json.dumps(options)
        )
        
        parsed_options = json.loads(question.options)
        assert len(parsed_options) == 3
        assert "选项A" in parsed_options

    def test_question_parent_child_relationship(self, db_session):
        """测试父子题目关系"""
        parent_question = Question(
            text="父题目",
            type="single_choice",
            options=json.dumps(["是", "否"]),
            owner_id=1
        )
        
        child_question = Question(
            text="子题目",
            type="conditional",
            parent_question_id=parent_question.id,
            trigger_options=json.dumps(["否"]),
            owner_id=1
        )
        
        db_session.add(parent_question)
        db_session.add(child_question)
        db_session.commit()
        
        assert child_question.parent_question_id == parent_question.id
