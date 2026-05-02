# Survey Product - Entity Relationship Diagram

```mermaid
erDiagram
    users {
        SERIAL id PK
        VARCHAR_255 username UK
        VARCHAR_255 email UK
        VARCHAR_255 hashed_password
        VARCHAR_50 role "researcher"
        BOOLEAN is_active "true"
        INTEGER organization_id FK
        INTEGER manager_id FK
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    organizations {
        SERIAL id PK
        VARCHAR_255 name UK
        TEXT description
        INTEGER owner_id FK "NOT NULL"
        BOOLEAN is_active
        BOOLEAN is_public
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    organization_members {
        SERIAL id PK
        INTEGER organization_id FK "NOT NULL"
        INTEGER user_id FK "NOT NULL"
        VARCHAR_50 role "member"
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    departments {
        SERIAL id PK
        VARCHAR_255 name
        VARCHAR_50 code
        TEXT description
        INTEGER organization_id FK "NOT NULL"
        INTEGER parent_id FK "self-ref"
        INTEGER level
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    categories {
        SERIAL id PK
        VARCHAR_255 name
        TEXT description
        VARCHAR_50 code
        INTEGER organization_id FK
        INTEGER parent_id FK "self-ref"
        INTEGER level
        VARCHAR_500 path
        INTEGER sort_order
        BOOLEAN is_active
        INTEGER created_by FK
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    tags {
        SERIAL id PK
        VARCHAR_100 name UK
        VARCHAR_20 color "#409EFF"
        TEXT description
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    questions {
        SERIAL id PK
        TEXT text
        VARCHAR_20 type "SINGLE_CHOICE, MULTI_CHOICE, TEXT_INPUT, NUMBER_INPUT"
        TEXT options "JSON"
        BOOLEAN is_required
        INTEGER order
        INTEGER usage_count "default 0"
        INTEGER min_score
        INTEGER max_score
        INTEGER owner_id FK
        INTEGER organization_id FK
        INTEGER category_id FK
        INTEGER parent_question_id FK "self-ref"
        TEXT trigger_options "JSON"
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    question_tags {
        INTEGER question_id PK_FK
        INTEGER tag_id PK_FK
    }

    surveys {
        SERIAL id PK
        VARCHAR_255 title
        TEXT description
        VARCHAR_50 status "pending, active, completed"
        INTEGER created_by_user_id FK "NOT NULL"
        INTEGER organization_id FK
        TIMESTAMP start_time
        TIMESTAMP end_time
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    participants {
        SERIAL id PK
        VARCHAR_255 name
        INTEGER department_id FK
        VARCHAR_255 position
        VARCHAR_255 email
        VARCHAR_50 phone
        INTEGER organization_id FK "NOT NULL"
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    survey_questions {
        SERIAL id PK
        INTEGER survey_id FK "NOT NULL"
        INTEGER question_id FK "NOT NULL"
        INTEGER order "NOT NULL"
        TIMESTAMP created_at
    }

    survey_answers {
        SERIAL id PK
        INTEGER survey_id FK
        INTEGER user_id FK
        INTEGER participant_id FK
        TIMESTAMP submitted_at
        TEXT answers "JSON"
        INTEGER total_score
        TEXT department
        TEXT position
        INTEGER organization_id FK
        TEXT organization_name
    }

    options {
        SERIAL id PK
        INTEGER question_id FK "NOT NULL"
        TEXT option_text
        VARCHAR_255 option_value
    }

    %% Self-referencing relationships
    users ||--o{ users : "manager_id -> subordinates"
    departments ||--o{ departments : "parent_id -> children"
    categories ||--o{ categories : "parent_id -> children"
    questions ||--o{ questions : "parent_question_id -> children"

    %% Organization relationships
    organizations ||--o{ users : "organization_id"
    organizations ||--o{ organization_members : "organization_id"
    organizations ||--o{ departments : "organization_id"
    organizations ||--o{ categories : "organization_id"
    organizations ||--o{ questions : "organization_id"
    organizations ||--o{ surveys : "organization_id"
    organizations ||--o{ participants : "organization_id"
    organizations ||--o{ survey_answers : "organization_id"

    %% User relationships
    users ||--o{ organization_members : "user_id"
    users ||--o{ questions : "owner_id"
    users ||--o{ surveys : "created_by_user_id"
    users ||--o{ survey_answers : "user_id"
    users ||--o{ categories : "created_by"

    %% Organization owner
    users ||--o{ organizations : "owner_id"

    %% Question relationships
    questions ||--o{ question_tags : "question_id"
    questions ||--o{ options : "question_id"
    questions ||--o{ survey_questions : "question_id"
    categories ||--o{ questions : "category_id"

    %% Tag relationships
    tags ||--o{ question_tags : "tag_id"

    %% Survey relationships
    surveys ||--o{ survey_questions : "survey_id"
    surveys ||--o{ survey_answers : "survey_id"

    %% Participant relationships
    participants ||--o{ survey_answers : "participant_id"
    departments ||--o{ participants : "department_id"
```

## Relationships Summary

| Relationship | Type | Description |
|---|---|---|
| users <-> organizations | Many-to-Many | via `organization_members` junction table |
| users -> users | Self-ref | `manager_id` for hierarchical management |
| organizations -> users | One-to-Many | `owner_id` (organization owner) |
| organizations -> departments | One-to-Many | departments belong to an organization |
| departments -> departments | Self-ref | `parent_id` for hierarchical departments |
| organizations -> categories | One-to-Many | categories belong to an organization |
| categories -> categories | Self-ref | `parent_id` for hierarchical categories |
| categories -> questions | One-to-Many | questions categorized under a category |
| questions -> tags | Many-to-Many | via `question_tags` junction table |
| questions -> questions | Self-ref | `parent_question_id` for conditional logic |
| questions -> options | One-to-Many | individual answer options per question |
| surveys -> questions | Many-to-Many | via `survey_questions` junction table |
| surveys -> survey_answers | One-to-Many | submitted responses per survey |
| users -> survey_answers | One-to-Many | answers submitted by a user |
| participants -> survey_answers | One-to-Many | answers from a participant (QR scan) |
| departments -> participants | One-to-Many | participants belong to a department |
