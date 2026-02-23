-- PostgreSQL database schema for survey_product
-- This file contains PostgreSQL-compatible table definitions

-- Drop existing tables if they exist (for clean migration)
DROP TABLE IF EXISTS survey_answers CASCADE;
DROP TABLE IF EXISTS survey_questions CASCADE;
DROP TABLE IF EXISTS question_tags CASCADE;
DROP TABLE IF EXISTS surveys CASCADE;
DROP TABLE IF EXISTS participants CASCADE;
DROP TABLE IF EXISTS organizations CASCADE;
DROP TABLE IF EXISTS organization_members CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS alembic_version CASCADE;

-- Create alembic version table
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    PRIMARY KEY (version_num)
);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    organization_id INTEGER NULL,
    manager_id INTEGER NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Create organizations table
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL,
    owner_id INTEGER NOT NULL,
    is_active BOOLEAN DEFAULT NULL,
    is_public BOOLEAN DEFAULT NULL
);

-- Create organization_members table
CREATE TABLE organization_members (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    UNIQUE (organization_id, user_id)
);

-- Create departments table
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NULL,
    description TEXT,
    organization_id INTEGER NOT NULL,
    parent_id INTEGER NULL,
    level INTEGER NULL,
    is_active BOOLEAN DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create categories table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    code VARCHAR(50) NULL,
    organization_id INTEGER NULL,
    parent_id INTEGER NULL,
    level INTEGER NULL,
    path VARCHAR(500) NULL,
    sort_order INTEGER NULL,
    is_active BOOLEAN DEFAULT NULL,
    created_by INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tags table
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    color VARCHAR(20) DEFAULT '#409EFF',
    description TEXT,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create questions table
CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    type VARCHAR(20) NOT NULL CHECK (type IN ('SINGLE_CHOICE', 'MULTI_CHOICE', 'TEXT_INPUT', 'NUMBER_INPUT')),
    options TEXT,
    is_required BOOLEAN DEFAULT NULL,
    "order" INTEGER NULL,
    owner_id INTEGER NULL,
    organization_id INTEGER NULL,
    category_id INTEGER NULL,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    min_score INTEGER NULL,
    max_score INTEGER NULL
);

-- Create surveys table
CREATE TABLE surveys (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by_user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    organization_id INTEGER NULL,
    status VARCHAR(50) NOT NULL
);

-- Create participants table
CREATE TABLE participants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department_id INTEGER NULL,
    position VARCHAR(255) NULL,
    email VARCHAR(255) NULL,
    phone VARCHAR(50) NULL,
    organization_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create question_tags table (many-to-many relationship)
CREATE TABLE question_tags (
    question_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (question_id, tag_id)
);

-- Create survey_questions table
CREATE TABLE survey_questions (
    id SERIAL PRIMARY KEY,
    survey_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    "order" INTEGER NOT NULL,
    created_at TIMESTAMP NULL
);

-- Create survey_answers table
CREATE TABLE survey_answers (
    id SERIAL PRIMARY KEY,
    survey_id INTEGER NULL,
    user_id INTEGER NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    answers TEXT NOT NULL,
    participant_id INTEGER NULL,
    total_score INTEGER NULL,
    department TEXT,
    position TEXT
);

-- Add indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_organization_id ON users(organization_id);
CREATE INDEX idx_users_manager_id ON users(manager_id);

CREATE INDEX idx_organizations_name ON organizations(name);
CREATE INDEX idx_organizations_owner_id ON organizations(owner_id);

CREATE INDEX idx_organization_members_organization_id ON organization_members(organization_id);
CREATE INDEX idx_organization_members_user_id ON organization_members(user_id);

CREATE INDEX idx_departments_organization_id ON departments(organization_id);
CREATE INDEX idx_departments_parent_id ON departments(parent_id);

CREATE INDEX idx_categories_organization_id ON categories(organization_id);
CREATE INDEX idx_categories_parent_id ON categories(parent_id);
CREATE INDEX idx_categories_created_by ON categories(created_by);

CREATE INDEX idx_questions_owner_id ON questions(owner_id);
CREATE INDEX idx_questions_organization_id ON questions(organization_id);
CREATE INDEX idx_questions_category_id ON questions(category_id);

CREATE INDEX idx_surveys_created_by_user_id ON surveys(created_by_user_id);
CREATE INDEX idx_surveys_organization_id ON surveys(organization_id);

CREATE INDEX idx_participants_department_id ON participants(department_id);
CREATE INDEX idx_participants_organization_id ON participants(organization_id);

CREATE INDEX idx_survey_answers_survey_id ON survey_answers(survey_id);
CREATE INDEX idx_survey_answers_user_id ON survey_answers(user_id);
CREATE INDEX idx_survey_answers_participant_id ON survey_answers(participant_id);

CREATE INDEX idx_survey_questions_survey_id ON survey_questions(survey_id);
CREATE INDEX idx_survey_questions_question_id ON survey_questions(question_id);

CREATE INDEX idx_question_tags_question_id ON question_tags(question_id);
CREATE INDEX idx_question_tags_tag_id ON question_tags(tag_id);

CREATE INDEX idx_tags_name ON tags(name);

-- Add foreign key constraints
ALTER TABLE users ADD CONSTRAINT fk_users_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
ALTER TABLE users ADD CONSTRAINT fk_users_manager_id 
    FOREIGN KEY (manager_id) REFERENCES users(id);

ALTER TABLE organizations ADD CONSTRAINT fk_organizations_owner_id 
    FOREIGN KEY (owner_id) REFERENCES users(id);

ALTER TABLE organization_members ADD CONSTRAINT fk_organization_members_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
ALTER TABLE organization_members ADD CONSTRAINT fk_organization_members_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id);

ALTER TABLE departments ADD CONSTRAINT fk_departments_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
ALTER TABLE departments ADD CONSTRAINT fk_departments_parent_id 
    FOREIGN KEY (parent_id) REFERENCES departments(id);

ALTER TABLE categories ADD CONSTRAINT fk_categories_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
ALTER TABLE categories ADD CONSTRAINT fk_categories_parent_id 
    FOREIGN KEY (parent_id) REFERENCES categories(id);
ALTER TABLE categories ADD CONSTRAINT fk_categories_created_by 
    FOREIGN KEY (created_by) REFERENCES users(id);

ALTER TABLE questions ADD CONSTRAINT fk_questions_owner_id 
    FOREIGN KEY (owner_id) REFERENCES users(id);
ALTER TABLE questions ADD CONSTRAINT fk_questions_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);
ALTER TABLE questions ADD CONSTRAINT fk_questions_category_id 
    FOREIGN KEY (category_id) REFERENCES categories(id);

ALTER TABLE surveys ADD CONSTRAINT fk_surveys_created_by_user_id 
    FOREIGN KEY (created_by_user_id) REFERENCES users(id);
ALTER TABLE surveys ADD CONSTRAINT fk_surveys_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);

ALTER TABLE participants ADD CONSTRAINT fk_participants_department_id 
    FOREIGN KEY (department_id) REFERENCES departments(id);
ALTER TABLE participants ADD CONSTRAINT fk_participants_organization_id 
    FOREIGN KEY (organization_id) REFERENCES organizations(id);

ALTER TABLE question_tags ADD CONSTRAINT fk_question_tags_question_id 
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE;
ALTER TABLE question_tags ADD CONSTRAINT fk_question_tags_tag_id 
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE;

ALTER TABLE survey_questions ADD CONSTRAINT fk_survey_questions_survey_id 
    FOREIGN KEY (survey_id) REFERENCES surveys(id);
ALTER TABLE survey_questions ADD CONSTRAINT fk_survey_questions_question_id 
    FOREIGN KEY (question_id) REFERENCES questions(id);

ALTER TABLE survey_answers ADD CONSTRAINT fk_survey_answers_survey_id 
    FOREIGN KEY (survey_id) REFERENCES surveys(id);
ALTER TABLE survey_answers ADD CONSTRAINT fk_survey_answers_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id);
ALTER TABLE survey_answers ADD CONSTRAINT fk_survey_answers_participant_id 
    FOREIGN KEY (participant_id) REFERENCES participants(id);

-- Insert initial alembic version
INSERT INTO alembic_version (version_num) VALUES ('1a2b3c4d5e6f');