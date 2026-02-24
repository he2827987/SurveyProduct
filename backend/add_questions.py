#!/usr/bin/env python3
"""
Script to add questions with creator ID=2 using the updated database models
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models_updated import User, Question, Tag, QuestionTag, Category, Organization
from backend.app.database import DATABASE_URL
import json

def add_questions_with_creator_2():
    """
    Add sample questions with creator ID=2
    """
    # Create database engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if user with ID=2 exists
        user = db.query(User).filter(User.id == 2).first()
        if not user:
            print("User with ID=2 not found. Please create this user first.")
            return
        
        print(f"Found user: {user.username} with ID={user.id}")
        
        # Get available tags and organizations
        tags = db.query(Tag).all()
        organizations = db.query(Organization).all()
        categories = db.query(Category).all()
        
        # Create sample questions
        sample_questions = [
            {
                "text": "您对公司的工作环境满意度如何？",
                "type": "SINGLE_CHOICE",
                "options": json.dumps(["非常满意", "满意", "一般", "不满意", "非常不满意"]),
                "is_required": True,
                "min_score": 1,
                "max_score": 5
            },
            {
                "text": "您认为公司需要改进的方面有哪些？（可多选）",
                "type": "MULTI_CHOICE",
                "options": json.dumps(["薪资待遇", "工作环境", "管理制度", "团队氛围", "发展机会", "工作内容"]),
                "is_required": False
            },
            {
                "text": "您对公司的建议或意见：",
                "type": "TEXT_INPUT",
                "is_required": False
            },
            {
                "text": "您在公司工作了多少年？",
                "type": "NUMBER_INPUT",
                "is_required": True
            },
            {
                "text": "您认为公司的培训体系是否完善？",
                "type": "SINGLE_CHOICE",
                "options": json.dumps(["非常完善", "比较完善", "一般", "不太完善", "非常不完善"]),
                "is_required": True,
                "min_score": 1,
                "max_score": 5
            }
        ]
        
        # Add questions to database
        added_questions = []
        for q_data in sample_questions:
            question = Question(
                text=q_data["text"],
                type=q_data["type"],
                options=q_data.get("options"),
                is_required=q_data.get("is_required", False),
                min_score=q_data.get("min_score"),
                max_score=q_data.get("max_score"),
                owner_id=user.id,  # Set creator ID to 2
                organization_id=organizations[0].id if organizations else None,
                category_id=categories[0].id if categories else None
            )
            
            db.add(question)
            db.commit()
            db.refresh(question)
            
            # Add tags to the question
            if tags:
                # Add first 2 tags to each question as example
                for tag in tags[:2]:
                    question_tag = QuestionTag(
                        question_id=question.id,
                        tag_id=tag.id
                    )
                    db.add(question_tag)
            
            added_questions.append(question)
            print(f"Added question: {question.text} (ID: {question.id})")
        
        db.commit()
        print(f"\nSuccessfully added {len(added_questions)} questions with creator ID=2!")
        
    except Exception as e:
        print(f"Error adding questions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_questions_with_creator_2()
