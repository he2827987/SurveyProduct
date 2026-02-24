# Database Models Comparison

## Overview
The original models.py file was basic and missing many features mentioned in the bug list. The updated models_updated.py file includes all the advanced features found in the current database schema.

## Key Differences

### Original Models (models.py)
- Basic User, Survey, Question, Answer, Organization models
- No support for tags, categories, departments
- No scoring system for questions
- No hierarchical organization structure
- Limited relationships between entities

### Updated Models (models_updated.py)
- Complete set of models matching the current database schema
- Added support for all features mentioned in the bug list

## New Features Added

### 1. Tags System
- **Tag model**: Stores tags with name, color, and description
- **QuestionTag model**: Many-to-many relationship between questions and tags
- Each question can have multiple tags for better organization

### 2. Scoring System
- **Question model**: Added `min_score` and `max_score` fields
- **Answer model**: Added `total_score` field for calculating survey scores

### 3. Categories
- **Category model**: Hierarchical categories with parent-child relationships
- Fields: `parent_id`, `level`, `path` for hierarchy
- Each category can be associated with an organization

### 4. Departments
- **Department model**: Hierarchical department structure
- Fields: `parent_id`, `level` for hierarchy
- Linked to organizations and participants

### 5. Organizations (Enhanced)
- **Organization model**: Now includes:
  - `owner_id`: Links to the user who owns the organization
  - `is_active`, `is_public`: Control visibility and status
- **OrganizationMember model**: Manages user roles within organizations

### 6. Participants
- **Participant model**: Represents survey participants
- Linked to departments and organizations
- Includes contact information

### 7. Enhanced Survey Structure
- **Survey model**: Added `status` and `organization_id` fields
- **SurveyQuestion model**: Separate table for survey-question relationships
- Supports ordering of questions within surveys

### 8. Question Types
- **Question model**: Now supports specific enum types:
  - SINGLE_CHOICE
  - MULTI_CHOICE
  - TEXT_INPUT
  - NUMBER_INPUT
- **options field**: Stores options as JSON for choice questions

### 9. Enhanced User Model
- Added `role`, `organization_id`, `manager_id`, `is_active` fields
- Support for organizational hierarchy and user management

## Using the Updated Models

### 1. Replace the old models file
```bash
# Backup the old models file
cp backend/app/models.py backend/app/models_original.py

# Use the updated models
cp backend/app/models_updated.py backend/app/models.py
```

### 2. Adding Questions with Creator ID=2
Use the provided script:
```bash
python backend/add_questions.py
```

### 3. Example: Creating a Question with Tags and Scores
```python
from backend.app.models import Question, Tag, QuestionTag
import json

# Create a question with scoring
question = Question(
    text="How satisfied are you with our product?",
    type="SINGLE_CHOICE",
    options=json.dumps(["Very Satisfied", "Satisfied", "Neutral", "Unsatisfied", "Very Unsatisfied"]),
    is_required=True,
    min_score=1,
    max_score=5,
    owner_id=2  # Set creator ID to 2
)

# Add tags to the question
tags = db.query(Tag).all()
for tag in tags:
    question_tag = QuestionTag(
        question_id=question.id,
        tag_id=tag.id
    )
    db.add(question_tag)
```

## Migration Notes

The database schema has evolved through several migrations:
1. Initial migration (1a2b3c4d5e6f): Created all tables
2. Added questions relationship to User model (c129020b449a)
3. Added department and participant models (708e4cafe87f)

## Database Schema Files

For complete schema details, refer to:
- `/postgresql_schema.sql` - PostgreSQL schema definition
- `/db_dump.sql` - MySQL dump with sample data
- `/alembic/versions/` - Migration files showing schema evolution

## Conclusion

The updated models provide a complete foundation for all features mentioned in the bug list:
- Tags functionality for categorizing questions
- Scoring system for questions and surveys
- Hierarchical organization structure with departments and categories
- Enhanced user management with roles and permissions
- Complete survey creation and management system

Use these models for any new development or scripts that need to interact with the database.
