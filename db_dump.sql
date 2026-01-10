-- MySQL dump 10.13  Distrib 9.3.0, for macos15.2 (arm64)
--
-- Host: localhost    Database: survey_db
-- ------------------------------------------------------
-- Server version	9.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('bbdef0aeda07');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text,
  `code` varchar(50) DEFAULT NULL,
  `organization_id` int DEFAULT NULL,
  `parent_id` int DEFAULT NULL,
  `level` int DEFAULT NULL,
  `path` varchar(500) DEFAULT NULL,
  `sort_order` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `organization_id` (`organization_id`),
  KEY `parent_id` (`parent_id`),
  KEY `created_by` (`created_by`),
  KEY `ix_categories_id` (`id`),
  CONSTRAINT `categories_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  CONSTRAINT `categories_ibfk_2` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `categories_ibfk_3` FOREIGN KEY (`created_by`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (1,'员工满意度调研','用于评估员工对工作各方面的满意度','EMP_SAT',NULL,NULL,1,NULL,1,1,3,'2025-08-20 14:28:51','2025-08-20 14:28:51'),(2,'工作环境与氛围','更新后的描述：工作环境和团队氛围相关的满意度调查','WORK_ENV',NULL,3,2,'3',1,1,3,'2025-08-20 14:28:51','2025-08-20 14:28:51'),(3,'产品反馈','产品相关的反馈和建议','PROD_FEED',NULL,NULL,1,NULL,2,1,3,'2025-08-20 14:28:51','2025-08-20 14:28:51'),(4,'员工满意度调研','用于评估员工对工作各方面的满意度','EMP_SAT',NULL,NULL,1,NULL,1,1,3,'2025-08-20 14:32:28','2025-08-20 14:32:28'),(5,'工作环境与氛围','更新后的描述：工作环境和团队氛围相关的满意度调查','WORK_ENV',NULL,6,2,'6',1,1,3,'2025-08-20 14:32:28','2025-08-20 14:32:28'),(6,'产品反馈','产品相关的反馈和建议','PROD_FEED',NULL,NULL,1,NULL,2,1,3,'2025-08-20 14:32:28','2025-08-20 14:32:28'),(7,'测试分类',NULL,NULL,NULL,NULL,1,NULL,0,1,2,'2025-08-20 14:37:22','2025-08-20 14:37:22'),(8,'测试子分类',NULL,NULL,NULL,7,2,'7',0,0,2,'2025-08-20 14:49:27','2025-08-20 14:49:27');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `departments`
--

DROP TABLE IF EXISTS `departments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `departments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `code` varchar(50) DEFAULT NULL,
  `description` text,
  `organization_id` int NOT NULL,
  `parent_id` int DEFAULT NULL,
  `level` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `organization_id` (`organization_id`),
  KEY `parent_id` (`parent_id`),
  KEY `ix_departments_id` (`id`),
  CONSTRAINT `departments_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  CONSTRAINT `departments_ibfk_2` FOREIGN KEY (`parent_id`) REFERENCES `departments` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `departments`
--

LOCK TABLES `departments` WRITE;
/*!40000 ALTER TABLE `departments` DISABLE KEYS */;
/*!40000 ALTER TABLE `departments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organization_members`
--

DROP TABLE IF EXISTS `organization_members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organization_members` (
  `id` int NOT NULL AUTO_INCREMENT,
  `organization_id` int NOT NULL,
  `user_id` int NOT NULL,
  `role` varchar(50) NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `_organization_user_uc` (`organization_id`,`user_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_organization_members_id` (`id`),
  CONSTRAINT `organization_members_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  CONSTRAINT `organization_members_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `organization_members`
--

LOCK TABLES `organization_members` WRITE;
/*!40000 ALTER TABLE `organization_members` DISABLE KEYS */;
INSERT INTO `organization_members` VALUES (12,13,3,'owner','2025-08-22 12:12:17',NULL),(13,14,3,'owner','2025-08-22 12:12:17',NULL),(14,15,3,'owner','2025-08-22 12:12:17',NULL),(15,16,3,'owner','2025-08-22 12:12:17',NULL),(16,17,3,'owner','2025-08-23 13:36:55',NULL);
/*!40000 ALTER TABLE `organization_members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `organizations`
--

DROP TABLE IF EXISTS `organizations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `organizations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `description` text,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `owner_id` int NOT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_public` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_organizations_name` (`name`),
  KEY `ix_organizations_id` (`id`),
  KEY `owner_id` (`owner_id`),
  CONSTRAINT `organizations_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `organizations`
--

LOCK TABLES `organizations` WRITE;
/*!40000 ALTER TABLE `organizations` DISABLE KEYS */;
INSERT INTO `organizations` VALUES (13,'腾讯科技','腾讯科技是一家知名的科技公司','2025-08-22 04:08:41','2025-08-22 04:08:41',3,1,0),(14,'阿里巴巴','阿里巴巴是一家知名的科技公司','2025-08-22 04:08:41','2025-08-22 04:08:41',3,1,0),(15,'字节跳动','字节跳动是一家知名的科技公司','2025-08-22 04:08:41','2025-08-22 04:08:41',3,1,0),(16,'百度科技','百度科技是一家知名的科技公司','2025-08-22 04:08:41','2025-08-22 04:08:41',3,1,0),(17,'百度','百度公司','2025-08-23 05:36:44','2025-08-23 05:36:44',3,1,0);
/*!40000 ALTER TABLE `organizations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `participants`
--

DROP TABLE IF EXISTS `participants`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `participants` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `department_id` int DEFAULT NULL,
  `position` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `organization_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `department_id` (`department_id`),
  KEY `organization_id` (`organization_id`),
  KEY `ix_participants_id` (`id`),
  CONSTRAINT `participants_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`id`),
  CONSTRAINT `participants_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=34 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `participants`
--

LOCK TABLES `participants` WRITE;
/*!40000 ALTER TABLE `participants` DISABLE KEYS */;
/*!40000 ALTER TABLE `participants` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `question_tags`
--

DROP TABLE IF EXISTS `question_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `question_tags` (
  `question_id` int NOT NULL,
  `tag_id` int NOT NULL,
  PRIMARY KEY (`question_id`,`tag_id`),
  KEY `idx_question_tags_question_id` (`question_id`),
  KEY `idx_question_tags_tag_id` (`tag_id`),
  CONSTRAINT `question_tags_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `question_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `question_tags`
--

LOCK TABLES `question_tags` WRITE;
/*!40000 ALTER TABLE `question_tags` DISABLE KEYS */;
INSERT INTO `question_tags` VALUES (102,1);
/*!40000 ALTER TABLE `question_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions`
--

DROP TABLE IF EXISTS `questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `text` text NOT NULL,
  `type` enum('SINGLE_CHOICE','MULTI_CHOICE','TEXT_INPUT','NUMBER_INPUT') NOT NULL,
  `options` text,
  `is_required` tinyint(1) DEFAULT NULL,
  `order` int DEFAULT NULL,
  `owner_id` int DEFAULT NULL,
  `organization_id` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `usage_count` int DEFAULT '0',
  `created_at` datetime DEFAULT CURRENT_TIMESTAMP,
  `updated_at` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `min_score` int DEFAULT NULL,
  `max_score` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_questions_id` (`id`),
  KEY `owner_id` (`owner_id`),
  KEY `organization_id` (`organization_id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `questions_ibfk_2` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`),
  CONSTRAINT `questions_ibfk_3` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  CONSTRAINT `questions_ibfk_4` FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=123 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions`
--

LOCK TABLES `questions` WRITE;
/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (36,'您认为公司的薪资待遇如何？','SINGLE_CHOICE','[\"\\u5f88\\u6709\\u7ade\\u4e89\\u529b\", \"\\u6709\\u7ade\\u4e89\\u529b\", \"\\u4e00\\u822c\", \"\\u504f\\u4f4e\", \"\\u5f88\\u4f4e\"]',0,2,2,NULL,NULL,83,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(38,'您认为公司需要改进的方面有哪些？（可多选）','MULTI_CHOICE','[\"\\u85aa\\u8d44\\u5f85\\u9047\", \"\\u5de5\\u4f5c\\u73af\\u5883\", \"\\u7ba1\\u7406\\u5236\\u5ea6\", \"\\u56e2\\u961f\\u6c1b\\u56f4\", \"\\u53d1\\u5c55\\u673a\\u4f1a\", \"\\u5de5\\u4f5c\\u5185\\u5bb9\"]',0,4,2,NULL,NULL,62,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(74,'测试1','SINGLE_CHOICE','[\"选项A\", \"选项B\", \"选项C\"]',0,1,2,NULL,NULL,12,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(75,'测试2','MULTI_CHOICE','[\"选项A\", \"选项B\", \"选项C\"]',0,2,2,NULL,NULL,8,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(76,'测试3','TEXT_INPUT',NULL,0,3,2,NULL,NULL,8,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(81,'您对当前工作环境的满意度如何？（已更新）','MULTI_CHOICE','[\"\\u9009\\u9879A\", \"\\u9009\\u9879B\", \"\\u9009\\u9879C\", \"\\u9009\\u9879D\"]',1,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(82,'您最喜欢公司的哪些方面？（可多选）','MULTI_CHOICE','[\"工作环境\", \"团队氛围\", \"薪资待遇\", \"发展机会\", \"工作内容\"]',0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(83,'您对公司的建议或意见：','TEXT_INPUT',NULL,0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(84,'您在公司工作了多少年？','NUMBER_INPUT',NULL,1,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(85,'您认为公司最需要改进的方面是什么？','TEXT_INPUT',NULL,0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(86,'您对公司的工作环境满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(87,'您对薪资福利的满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(88,'您认为公司最需要改进的方面是什么？','TEXT_INPUT',NULL,0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(89,'您对公司的工作环境满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(90,'您对薪资福利的满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(91,'您认为公司最需要改进的方面是什么？','TEXT_INPUT',NULL,0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(92,'您对公司的工作环境满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(93,'您对薪资福利的满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(94,'您认为公司最需要改进的方面是什么？','TEXT_INPUT',NULL,0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(95,'您对公司的工作环境满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,1,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(96,'您对薪资福利的满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,1,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(97,'您对公司的工作环境满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,1,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(98,'您对薪资福利的满意度如何？','SINGLE_CHOICE','[\"非常满意\", \"满意\", \"一般\", \"不满意\", \"非常不满意\"]',0,0,3,NULL,NULL,1,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(99,'测试题目','SINGLE_CHOICE','[\"选项A\", \"选项B\", \"选项C\"]',0,0,3,NULL,NULL,0,'2025-08-27 23:42:07','2025-08-27 23:42:07',NULL,NULL),(100,'测试题目2','SINGLE_CHOICE','[\"\\u9009\\u9879A\", \"\\u9009\\u9879B\", \"\\u9009\\u9879C\", \"\\u9009\\u9879D\", \"\\u9009\\u9879E\"]',0,0,2,NULL,NULL,0,'2025-12-06 07:06:14','2025-12-06 07:06:33',NULL,NULL),(101,'测试题目3','SINGLE_CHOICE','[{\"text\": \"选项A\", \"score\": 5}, {\"text\": \"选项B\", \"score\": 0}, {\"text\": \"选项C\", \"score\": -5}]',0,0,2,NULL,NULL,0,'2025-12-07 13:06:40','2025-12-07 13:06:40',-5,5),(102,'测试题目4','SINGLE_CHOICE','[{\"text\": \"选项A\", \"score\": 3, \"is_correct\": false}, {\"text\": \"选项B\", \"score\": 5, \"is_correct\": true}, {\"text\": \"选项C\", \"score\": 2, \"is_correct\": false}]',1,0,2,NULL,8,0,'2025-12-07 13:47:29','2025-12-08 13:36:05',0,10),(103,'Q1: 对产品满意度？','SINGLE_CHOICE','[{\"text\": \"非常满意\", \"score\": 10}, {\"text\": \"满意\", \"score\": 8}, {\"text\": \"一般\", \"score\": 6}, {\"text\": \"不满意\", \"score\": 3}]',0,1,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(104,'Q2: 对团队合作评价？','SINGLE_CHOICE','[{\"text\": \"优秀\", \"score\": 10}, {\"text\": \"良好\", \"score\": 8}, {\"text\": \"一般\", \"score\": 6}, {\"text\": \"较差\", \"score\": 3}]',0,2,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(105,'Q3: 对工作环境评价？','SINGLE_CHOICE','[{\"text\": \"很好\", \"score\": 9}, {\"text\": \"还行\", \"score\": 7}, {\"text\": \"一般\", \"score\": 5}, {\"text\": \"较差\", \"score\": 2}]',0,3,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(106,'Q4: 你认为哪些福利重要？','MULTI_CHOICE','[{\"text\": \"薪资\", \"score\": 5}, {\"text\": \"保险\", \"score\": 4}, {\"text\": \"弹性工作\", \"score\": 3}, {\"text\": \"培训\", \"score\": 2}]',0,4,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(107,'Q5: 你最关注的职业发展要素？','MULTI_CHOICE','[{\"text\": \"晋升\", \"score\": 5}, {\"text\": \"学习机会\", \"score\": 4}, {\"text\": \"项目挑战\", \"score\": 3}, {\"text\": \"领导支持\", \"score\": 2}]',0,5,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(108,'Q6: 对公司改进的建议？','TEXT_INPUT',NULL,0,6,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(109,'Q7: 你最想学习的技能？','TEXT_INPUT',NULL,0,7,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(110,'Q8: 对绩效考核认可度？','SINGLE_CHOICE','[{\"text\": \"认可\", \"score\": 8}, {\"text\": \"基本认可\", \"score\": 6}, {\"text\": \"一般\", \"score\": 4}, {\"text\": \"不认可\", \"score\": 2}]',0,8,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(111,'Q9: 你更看重的激励？','MULTI_CHOICE','[{\"text\": \"奖金\", \"score\": 4}, {\"text\": \"期权\", \"score\": 4}, {\"text\": \"表彰\", \"score\": 2}, {\"text\": \"休假\", \"score\": 3}]',0,9,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(112,'Q10: 目前最大的工作痛点？','TEXT_INPUT',NULL,0,10,2,NULL,NULL,0,'2025-12-09 13:14:57','2025-12-09 13:14:57',0,10),(113,'Q1: 对产品满意度？','SINGLE_CHOICE','[{\"text\": \"非常满意\", \"score\": 10}, {\"text\": \"满意\", \"score\": 8}, {\"text\": \"一般\", \"score\": 6}, {\"text\": \"不满意\", \"score\": 3}]',0,1,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10),(114,'Q2: 对团队合作评价？','SINGLE_CHOICE','[{\"text\": \"优秀\", \"score\": 10}, {\"text\": \"良好\", \"score\": 8}, {\"text\": \"一般\", \"score\": 6}, {\"text\": \"较差\", \"score\": 3}]',0,2,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10),(115,'Q3: 对工作环境评价？','SINGLE_CHOICE','[{\"text\": \"很好\", \"score\": 9}, {\"text\": \"还行\", \"score\": 7}, {\"text\": \"一般\", \"score\": 5}, {\"text\": \"较差\", \"score\": 2}]',0,3,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10),(116,'Q4: 你认为哪些福利重要？','MULTI_CHOICE','[{\"text\": \"薪资\", \"score\": 5}, {\"text\": \"保险\", \"score\": 4}, {\"text\": \"弹性工作\", \"score\": 3}, {\"text\": \"培训\", \"score\": 2}]',0,4,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10),(117,'Q5: 你最关注的职业发展要素？','MULTI_CHOICE','[{\"text\": \"晋升\", \"score\": 5}, {\"text\": \"学习机会\", \"score\": 4}, {\"text\": \"项目挑战\", \"score\": 3}, {\"text\": \"领导支持\", \"score\": 2}]',0,5,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10),(118,'Q6: 对公司改进的建议？','TEXT_INPUT',NULL,0,6,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10),(119,'Q7: 你最想学习的技能？','TEXT_INPUT',NULL,0,7,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10),(120,'Q8: 对绩效考核认可度？','SINGLE_CHOICE','[{\"text\": \"认可\", \"score\": 8}, {\"text\": \"基本认可\", \"score\": 6}, {\"text\": \"一般\", \"score\": 4}, {\"text\": \"不认可\", \"score\": 2}]',0,8,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10),(121,'Q9: 你更看重的激励？','MULTI_CHOICE','[{\"text\": \"奖金\", \"score\": 4}, {\"text\": \"期权\", \"score\": 4}, {\"text\": \"表彰\", \"score\": 2}, {\"text\": \"休假\", \"score\": 3}]',0,9,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10),(122,'Q10: 目前最大的工作痛点？','TEXT_INPUT',NULL,0,10,2,NULL,NULL,0,'2025-12-09 13:16:17','2025-12-09 13:16:17',0,10);
/*!40000 ALTER TABLE `questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `survey_answers`
--

DROP TABLE IF EXISTS `survey_answers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `survey_answers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `survey_id` int DEFAULT NULL,
  `user_id` int DEFAULT NULL,
  `submitted_at` datetime DEFAULT (now()),
  `answers` text NOT NULL,
  `participant_id` int DEFAULT NULL,
  `total_score` int DEFAULT NULL,
  `department` text,
  `position` text,
  PRIMARY KEY (`id`),
  KEY `survey_id` (`survey_id`),
  KEY `user_id` (`user_id`),
  KEY `ix_survey_answers_id` (`id`),
  KEY `participant_id` (`participant_id`),
  CONSTRAINT `survey_answers_ibfk_1` FOREIGN KEY (`survey_id`) REFERENCES `surveys` (`id`),
  CONSTRAINT `survey_answers_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `survey_answers_ibfk_3` FOREIGN KEY (`participant_id`) REFERENCES `participants` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=157 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `survey_answers`
--

LOCK TABLES `survey_answers` WRITE;
/*!40000 ALTER TABLE `survey_answers` DISABLE KEYS */;
INSERT INTO `survey_answers` VALUES (19,22,3,'2025-08-22 12:12:17','{\"1\": \"\\u6ee1\\u610f\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(20,22,3,'2025-08-22 12:12:17','{\"1\": \"\\u4e00\\u822c\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(21,22,3,'2025-08-22 12:12:17','{\"1\": \"\\u6ee1\\u610f\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(22,23,3,'2025-08-22 12:12:17','{\"1\": \"\\u6ee1\\u610f\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(23,23,3,'2025-08-22 12:12:17','{\"1\": \"\\u4e00\\u822c\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(24,23,3,'2025-08-22 12:12:17','{\"1\": \"\\u6ee1\\u610f\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(25,23,3,'2025-08-22 12:12:17','{\"1\": \"\\u4e00\\u822c\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(26,24,3,'2025-08-22 12:12:17','{\"1\": \"\\u6ee1\\u610f\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(27,24,3,'2025-08-22 12:12:17','{\"1\": \"\\u4e00\\u822c\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(28,24,3,'2025-08-22 12:12:17','{\"1\": \"\\u6ee1\\u610f\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(29,24,3,'2025-08-22 12:12:18','{\"1\": \"\\u4e00\\u822c\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(30,24,3,'2025-08-22 12:12:18','{\"1\": \"\\u6ee1\\u610f\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(31,25,3,'2025-08-22 12:12:18','{\"1\": \"\\u6ee1\\u610f\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(32,25,3,'2025-08-22 12:12:18','{\"1\": \"\\u4e00\\u822c\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(33,25,3,'2025-08-22 12:12:18','{\"1\": \"\\u6ee1\\u610f\", \"2\": \"\\u85aa\\u8d44\\u798f\\u5229\", \"3\": \"\\u5de5\\u4f5c\\u538b\\u529b\"}',NULL,NULL,NULL,NULL),(56,29,2,'2025-12-06 15:59:12','{\"74\": \"\\u9009\\u9879A\", \"75\": [\"\\u9009\\u9879B\"], \"76\": \"\\u6d4b\\u8bd5\"}',NULL,NULL,NULL,NULL),(57,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"良好\", \"115\": \"还行\", \"116\": [\"培训\", \"薪资\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 100\", \"119\": \"自由回答 2\", \"120\": \"一般\", \"121\": [\"期权\", \"休假\"], \"122\": \"自由回答 22\"}',NULL,38,'技术部','junior'),(58,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"良好\", \"115\": \"很好\", \"116\": [\"培训\", \"薪资\"], \"117\": [\"项目挑战\", \"学习机会\"], \"118\": \"自由回答 9\", \"119\": \"自由回答 60\", \"120\": \"不认可\", \"121\": [\"表彰\", \"期权\"], \"122\": \"自由回答 50\"}',NULL,47,'技术部','junior'),(59,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"良好\", \"115\": \"一般\", \"116\": [\"弹性工作\"], \"117\": [\"晋升\"], \"118\": \"自由回答 22\", \"119\": \"自由回答 91\", \"120\": \"不认可\", \"121\": [\"休假\", \"表彰\"], \"122\": \"自由回答 7\"}',NULL,34,'运营部','intern'),(60,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"良好\", \"115\": \"很好\", \"116\": [\"薪资\", \"培训\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 56\", \"119\": \"自由回答 32\", \"120\": \"一般\", \"121\": [\"期权\", \"休假\"], \"122\": \"自由回答 71\"}',NULL,42,'人事部','manager'),(61,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"较差\", \"115\": \"较差\", \"116\": [\"培训\"], \"117\": [\"学习机会\", \"晋升\"], \"118\": \"自由回答 69\", \"119\": \"自由回答 58\", \"120\": \"不认可\", \"121\": [\"休假\"], \"122\": \"自由回答 54\"}',NULL,24,'运营部','intern'),(62,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"一般\", \"115\": \"很好\", \"116\": [\"培训\", \"弹性工作\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 27\", \"119\": \"自由回答 35\", \"120\": \"基本认可\", \"121\": [\"休假\"], \"122\": \"自由回答 52\"}',NULL,39,'技术部','executive'),(63,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"较差\", \"115\": \"很好\", \"116\": [\"保险\", \"薪资\"], \"117\": [\"晋升\"], \"118\": \"自由回答 77\", \"119\": \"自由回答 68\", \"120\": \"不认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 28\"}',NULL,38,'产品部','junior'),(64,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"良好\", \"115\": \"较差\", \"116\": [\"弹性工作\", \"保险\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 7\", \"119\": \"自由回答 34\", \"120\": \"一般\", \"121\": [\"期权\"], \"122\": \"自由回答 12\"}',NULL,35,'市场部','intern'),(65,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"优秀\", \"115\": \"一般\", \"116\": [\"薪资\", \"培训\"], \"117\": [\"项目挑战\", \"学习机会\"], \"118\": \"自由回答 87\", \"119\": \"自由回答 50\", \"120\": \"一般\", \"121\": [\"休假\"], \"122\": \"自由回答 16\"}',NULL,42,'运营部','executive'),(66,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"还行\", \"116\": [\"培训\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 20\", \"119\": \"自由回答 66\", \"120\": \"认可\", \"121\": [\"休假\", \"期权\"], \"122\": \"自由回答 75\"}',NULL,39,'技术部','manager'),(67,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"优秀\", \"115\": \"一般\", \"116\": [\"保险\"], \"117\": [\"学习机会\", \"晋升\"], \"118\": \"自由回答 58\", \"119\": \"自由回答 81\", \"120\": \"认可\", \"121\": [\"奖金\", \"休假\"], \"122\": \"自由回答 87\"}',NULL,51,'技术部','intern'),(68,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"较差\", \"115\": \"还行\", \"116\": [\"保险\", \"培训\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 67\", \"119\": \"自由回答 17\", \"120\": \"认可\", \"121\": [\"期权\"], \"122\": \"自由回答 79\"}',NULL,36,'运营部','executive'),(69,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"良好\", \"115\": \"一般\", \"116\": [\"弹性工作\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 70\", \"119\": \"自由回答 69\", \"120\": \"一般\", \"121\": [\"表彰\", \"奖金\"], \"122\": \"自由回答 14\"}',NULL,39,'产品部','junior'),(70,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"较差\", \"115\": \"一般\", \"116\": [\"培训\", \"保险\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 75\", \"119\": \"自由回答 45\", \"120\": \"基本认可\", \"121\": [\"奖金\", \"表彰\"], \"122\": \"自由回答 66\"}',NULL,36,'市场部','intern'),(71,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"优秀\", \"115\": \"很好\", \"116\": [\"弹性工作\"], \"117\": [\"晋升\"], \"118\": \"自由回答 78\", \"119\": \"自由回答 85\", \"120\": \"基本认可\", \"121\": [\"奖金\", \"期权\"], \"122\": \"自由回答 52\"}',NULL,47,'技术部','junior'),(72,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"保险\"], \"117\": [\"学习机会\", \"晋升\"], \"118\": \"自由回答 27\", \"119\": \"自由回答 77\", \"120\": \"基本认可\", \"121\": [\"休假\"], \"122\": \"自由回答 70\"}',NULL,36,'人事部','junior'),(73,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"优秀\", \"115\": \"很好\", \"116\": [\"培训\", \"保险\"], \"117\": [\"晋升\", \"领导支持\"], \"118\": \"自由回答 49\", \"119\": \"自由回答 36\", \"120\": \"认可\", \"121\": [\"期权\", \"休假\"], \"122\": \"自由回答 90\"}',NULL,53,'运营部','executive'),(74,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"一般\", \"116\": [\"薪资\", \"弹性工作\"], \"117\": [\"领导支持\", \"项目挑战\"], \"118\": \"自由回答 96\", \"119\": \"自由回答 28\", \"120\": \"一般\", \"121\": [\"表彰\", \"奖金\"], \"122\": \"自由回答 47\"}',NULL,41,'运营部','executive'),(75,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"还行\", \"116\": [\"培训\", \"薪资\"], \"117\": [\"学习机会\", \"项目挑战\"], \"118\": \"自由回答 8\", \"119\": \"自由回答 6\", \"120\": \"基本认可\", \"121\": [\"期权\", \"休假\"], \"122\": \"自由回答 87\"}',NULL,47,'人事部','intern'),(76,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"还行\", \"116\": [\"弹性工作\"], \"117\": [\"项目挑战\", \"学习机会\"], \"118\": \"自由回答 83\", \"119\": \"自由回答 67\", \"120\": \"基本认可\", \"121\": [\"休假\"], \"122\": \"自由回答 48\"}',NULL,39,'财务部','junior'),(77,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"良好\", \"115\": \"很好\", \"116\": [\"薪资\"], \"117\": [\"领导支持\", \"晋升\"], \"118\": \"自由回答 86\", \"119\": \"自由回答 81\", \"120\": \"基本认可\", \"121\": [\"休假\", \"表彰\"], \"122\": \"自由回答 92\"}',NULL,43,'人事部','intern'),(78,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"优秀\", \"115\": \"还行\", \"116\": [\"弹性工作\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 5\", \"119\": \"自由回答 20\", \"120\": \"一般\", \"121\": [\"休假\", \"期权\"], \"122\": \"自由回答 2\"}',NULL,45,'市场部','executive'),(79,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"还行\", \"116\": [\"培训\", \"保险\"], \"117\": [\"晋升\", \"学习机会\"], \"118\": \"自由回答 4\", \"119\": \"自由回答 89\", \"120\": \"基本认可\", \"121\": [\"期权\", \"表彰\"], \"122\": \"自由回答 44\"}',NULL,47,'财务部','senior'),(80,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"一般\", \"115\": \"很好\", \"116\": [\"弹性工作\"], \"117\": [\"晋升\", \"学习机会\"], \"118\": \"自由回答 58\", \"119\": \"自由回答 71\", \"120\": \"一般\", \"121\": [\"期权\"], \"122\": \"自由回答 59\"}',NULL,43,'财务部','intern'),(81,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"较差\", \"115\": \"还行\", \"116\": [\"保险\", \"弹性工作\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 60\", \"119\": \"自由回答 33\", \"120\": \"认可\", \"121\": [\"表彰\", \"期权\"], \"122\": \"自由回答 49\"}',NULL,40,'财务部','senior'),(82,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"优秀\", \"115\": \"较差\", \"116\": [\"弹性工作\"], \"117\": [\"学习机会\", \"项目挑战\"], \"118\": \"自由回答 32\", \"119\": \"自由回答 50\", \"120\": \"一般\", \"121\": [\"期权\"], \"122\": \"自由回答 73\"}',NULL,40,'产品部','executive'),(83,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"还行\", \"116\": [\"弹性工作\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 91\", \"119\": \"自由回答 78\", \"120\": \"基本认可\", \"121\": [\"期权\"], \"122\": \"自由回答 9\"}',NULL,33,'技术部','junior'),(84,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"一般\", \"115\": \"很好\", \"116\": [\"弹性工作\", \"薪资\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 11\", \"119\": \"自由回答 68\", \"120\": \"一般\", \"121\": [\"奖金\"], \"122\": \"自由回答 56\"}',NULL,39,'财务部','senior'),(85,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"优秀\", \"115\": \"很好\", \"116\": [\"保险\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 86\", \"119\": \"自由回答 78\", \"120\": \"基本认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 7\"}',NULL,40,'产品部','senior'),(86,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"良好\", \"115\": \"一般\", \"116\": [\"保险\", \"弹性工作\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 33\", \"119\": \"自由回答 55\", \"120\": \"不认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 63\"}',NULL,30,'财务部','manager'),(87,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"薪资\", \"培训\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 2\", \"119\": \"自由回答 5\", \"120\": \"认可\", \"121\": [\"期权\", \"休假\"], \"122\": \"自由回答 46\"}',NULL,43,'运营部','junior'),(88,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"较差\", \"115\": \"较差\", \"116\": [\"培训\", \"弹性工作\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 98\", \"119\": \"自由回答 24\", \"120\": \"认可\", \"121\": [\"期权\"], \"122\": \"自由回答 59\"}',NULL,34,'技术部','senior'),(89,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"优秀\", \"115\": \"一般\", \"116\": [\"弹性工作\", \"培训\"], \"117\": [\"晋升\"], \"118\": \"自由回答 32\", \"119\": \"自由回答 20\", \"120\": \"一般\", \"121\": [\"表彰\"], \"122\": \"自由回答 82\"}',NULL,41,'市场部','junior'),(90,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"弹性工作\", \"薪资\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 71\", \"119\": \"自由回答 42\", \"120\": \"基本认可\", \"121\": [\"奖金\", \"休假\"], \"122\": \"自由回答 4\"}',NULL,39,'运营部','executive'),(91,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"较差\", \"115\": \"很好\", \"116\": [\"弹性工作\", \"保险\"], \"117\": [\"晋升\", \"学习机会\"], \"118\": \"自由回答 79\", \"119\": \"自由回答 73\", \"120\": \"认可\", \"121\": [\"休假\"], \"122\": \"自由回答 88\"}',NULL,47,'运营部','executive'),(92,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"较差\", \"115\": \"很好\", \"116\": [\"薪资\"], \"117\": [\"晋升\"], \"118\": \"自由回答 25\", \"119\": \"自由回答 48\", \"120\": \"一般\", \"121\": [\"表彰\"], \"122\": \"自由回答 58\"}',NULL,31,'人事部','senior'),(93,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"优秀\", \"115\": \"一般\", \"116\": [\"保险\", \"弹性工作\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 59\", \"119\": \"自由回答 10\", \"120\": \"不认可\", \"121\": [\"奖金\", \"休假\"], \"122\": \"自由回答 7\"}',NULL,42,'市场部','intern'),(94,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"很好\", \"116\": [\"薪资\", \"保险\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 76\", \"119\": \"自由回答 19\", \"120\": \"不认可\", \"121\": [\"期权\"], \"122\": \"自由回答 2\"}',NULL,35,'财务部','intern'),(95,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"较差\", \"116\": [\"薪资\", \"弹性工作\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 75\", \"119\": \"自由回答 78\", \"120\": \"认可\", \"121\": [\"休假\", \"表彰\"], \"122\": \"自由回答 67\"}',NULL,38,'人事部','executive'),(96,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"较差\", \"115\": \"很好\", \"116\": [\"薪资\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 7\", \"119\": \"自由回答 9\", \"120\": \"认可\", \"121\": [\"休假\"], \"122\": \"自由回答 32\"}',NULL,39,'运营部','junior'),(97,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"较差\", \"115\": \"较差\", \"116\": [\"培训\"], \"117\": [\"领导支持\", \"学习机会\"], \"118\": \"自由回答 27\", \"119\": \"自由回答 9\", \"120\": \"基本认可\", \"121\": [\"奖金\"], \"122\": \"自由回答 82\"}',NULL,29,'人事部','executive'),(98,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"较差\", \"116\": [\"保险\"], \"117\": [\"学习机会\", \"领导支持\"], \"118\": \"自由回答 79\", \"119\": \"自由回答 61\", \"120\": \"基本认可\", \"121\": [\"奖金\"], \"122\": \"自由回答 64\"}',NULL,35,'财务部','manager'),(99,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"较差\", \"115\": \"一般\", \"116\": [\"保险\"], \"117\": [\"晋升\"], \"118\": \"自由回答 68\", \"119\": \"自由回答 31\", \"120\": \"不认可\", \"121\": [\"期权\", \"表彰\"], \"122\": \"自由回答 60\"}',NULL,33,'财务部','manager'),(100,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"还行\", \"116\": [\"薪资\"], \"117\": [\"领导支持\", \"晋升\"], \"118\": \"自由回答 81\", \"119\": \"自由回答 88\", \"120\": \"一般\", \"121\": [\"奖金\", \"表彰\"], \"122\": \"自由回答 80\"}',NULL,38,'市场部','executive'),(101,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"较差\", \"115\": \"一般\", \"116\": [\"薪资\"], \"117\": [\"晋升\", \"项目挑战\"], \"118\": \"自由回答 29\", \"119\": \"自由回答 46\", \"120\": \"一般\", \"121\": [\"奖金\", \"表彰\"], \"122\": \"自由回答 94\"}',NULL,34,'人事部','executive'),(102,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"一般\", \"115\": \"还行\", \"116\": [\"培训\", \"弹性工作\"], \"117\": [\"领导支持\", \"学习机会\"], \"118\": \"自由回答 13\", \"119\": \"自由回答 66\", \"120\": \"认可\", \"121\": [\"奖金\"], \"122\": \"自由回答 67\"}',NULL,46,'产品部','intern'),(103,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"较差\", \"116\": [\"薪资\"], \"117\": [\"晋升\", \"领导支持\"], \"118\": \"自由回答 24\", \"119\": \"自由回答 43\", \"120\": \"不认可\", \"121\": [\"休假\"], \"122\": \"自由回答 99\"}',NULL,32,'技术部','senior'),(104,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"优秀\", \"115\": \"还行\", \"116\": [\"保险\", \"培训\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 31\", \"119\": \"自由回答 58\", \"120\": \"基本认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 9\"}',NULL,43,'技术部','senior'),(105,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"一般\", \"116\": [\"薪资\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 68\", \"119\": \"自由回答 63\", \"120\": \"基本认可\", \"121\": [\"奖金\", \"期权\"], \"122\": \"自由回答 82\"}',NULL,37,'市场部','intern'),(106,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"保险\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 57\", \"119\": \"自由回答 58\", \"120\": \"不认可\", \"121\": [\"休假\", \"表彰\"], \"122\": \"自由回答 15\"}',NULL,26,'运营部','executive'),(107,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"很好\", \"116\": [\"弹性工作\", \"保险\"], \"117\": [\"项目挑战\", \"晋升\"], \"118\": \"自由回答 62\", \"119\": \"自由回答 67\", \"120\": \"基本认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 40\"}',NULL,41,'运营部','manager'),(108,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"一般\", \"115\": \"还行\", \"116\": [\"培训\"], \"117\": [\"晋升\"], \"118\": \"自由回答 44\", \"119\": \"自由回答 62\", \"120\": \"基本认可\", \"121\": [\"休假\"], \"122\": \"自由回答 70\"}',NULL,39,'产品部','intern'),(109,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"良好\", \"115\": \"较差\", \"116\": [\"培训\"], \"117\": [\"领导支持\", \"项目挑战\"], \"118\": \"自由回答 35\", \"119\": \"自由回答 42\", \"120\": \"基本认可\", \"121\": [\"表彰\", \"休假\"], \"122\": \"自由回答 87\"}',NULL,31,'技术部','senior'),(110,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"良好\", \"115\": \"较差\", \"116\": [\"保险\", \"培训\"], \"117\": [\"晋升\", \"学习机会\"], \"118\": \"自由回答 9\", \"119\": \"自由回答 30\", \"120\": \"基本认可\", \"121\": [\"奖金\"], \"122\": \"自由回答 50\"}',NULL,45,'产品部','executive'),(111,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"较差\", \"115\": \"较差\", \"116\": [\"薪资\", \"培训\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 34\", \"119\": \"自由回答 93\", \"120\": \"基本认可\", \"121\": [\"期权\"], \"122\": \"自由回答 41\"}',NULL,36,'人事部','executive'),(112,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"优秀\", \"115\": \"很好\", \"116\": [\"保险\"], \"117\": [\"领导支持\", \"晋升\"], \"118\": \"自由回答 94\", \"119\": \"自由回答 15\", \"120\": \"认可\", \"121\": [\"休假\", \"奖金\"], \"122\": \"自由回答 64\"}',NULL,55,'市场部','intern'),(113,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"还行\", \"116\": [\"保险\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 91\", \"119\": \"自由回答 53\", \"120\": \"不认可\", \"121\": [\"休假\"], \"122\": \"自由回答 12\"}',NULL,32,'技术部','executive'),(114,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"较差\", \"115\": \"还行\", \"116\": [\"保险\"], \"117\": [\"学习机会\", \"领导支持\"], \"118\": \"自由回答 22\", \"119\": \"自由回答 96\", \"120\": \"认可\", \"121\": [\"期权\", \"休假\"], \"122\": \"自由回答 95\"}',NULL,43,'市场部','executive'),(115,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"良好\", \"115\": \"一般\", \"116\": [\"培训\", \"保险\"], \"117\": [\"项目挑战\", \"领导支持\"], \"118\": \"自由回答 83\", \"119\": \"自由回答 46\", \"120\": \"基本认可\", \"121\": [\"表彰\", \"期权\"], \"122\": \"自由回答 85\"}',NULL,44,'产品部','intern'),(116,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"良好\", \"115\": \"一般\", \"116\": [\"保险\"], \"117\": [\"晋升\"], \"118\": \"自由回答 83\", \"119\": \"自由回答 99\", \"120\": \"基本认可\", \"121\": [\"休假\", \"表彰\"], \"122\": \"自由回答 80\"}',NULL,43,'财务部','manager'),(117,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"优秀\", \"115\": \"很好\", \"116\": [\"薪资\", \"培训\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 96\", \"119\": \"自由回答 86\", \"120\": \"认可\", \"121\": [\"期权\", \"表彰\"], \"122\": \"自由回答 12\"}',NULL,53,'技术部','senior'),(118,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"很好\", \"116\": [\"薪资\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 56\", \"119\": \"自由回答 48\", \"120\": \"基本认可\", \"121\": [\"奖金\"], \"122\": \"自由回答 76\"}',NULL,39,'财务部','manager'),(119,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"优秀\", \"115\": \"较差\", \"116\": [\"培训\", \"薪资\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 50\", \"119\": \"自由回答 67\", \"120\": \"不认可\", \"121\": [\"期权\", \"表彰\"], \"122\": \"自由回答 77\"}',NULL,40,'市场部','manager'),(120,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"较差\", \"115\": \"一般\", \"116\": [\"薪资\"], \"117\": [\"学习机会\", \"晋升\"], \"118\": \"自由回答 62\", \"119\": \"自由回答 76\", \"120\": \"基本认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 58\"}',NULL,36,'产品部','intern'),(121,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"薪资\"], \"117\": [\"项目挑战\", \"领导支持\"], \"118\": \"自由回答 46\", \"119\": \"自由回答 1\", \"120\": \"一般\", \"121\": [\"奖金\"], \"122\": \"自由回答 12\"}',NULL,34,'运营部','junior'),(122,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"较差\", \"115\": \"较差\", \"116\": [\"薪资\"], \"117\": [\"晋升\", \"学习机会\"], \"118\": \"自由回答 19\", \"119\": \"自由回答 11\", \"120\": \"一般\", \"121\": [\"休假\", \"奖金\"], \"122\": \"自由回答 93\"}',NULL,40,'人事部','senior'),(123,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"培训\", \"保险\"], \"117\": [\"领导支持\", \"学习机会\"], \"118\": \"自由回答 58\", \"119\": \"自由回答 71\", \"120\": \"基本认可\", \"121\": [\"表彰\", \"期权\"], \"122\": \"自由回答 9\"}',NULL,40,'产品部','intern'),(124,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"一般\", \"115\": \"一般\", \"116\": [\"保险\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 19\", \"119\": \"自由回答 65\", \"120\": \"一般\", \"121\": [\"奖金\"], \"122\": \"自由回答 62\"}',NULL,32,'技术部','executive'),(125,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"优秀\", \"115\": \"很好\", \"116\": [\"薪资\", \"培训\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 42\", \"119\": \"自由回答 29\", \"120\": \"基本认可\", \"121\": [\"休假\"], \"122\": \"自由回答 30\"}',NULL,43,'人事部','manager'),(126,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"良好\", \"115\": \"很好\", \"116\": [\"培训\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 77\", \"119\": \"自由回答 68\", \"120\": \"基本认可\", \"121\": [\"期权\", \"奖金\"], \"122\": \"自由回答 18\"}',NULL,45,'产品部','manager'),(127,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"较差\", \"115\": \"较差\", \"116\": [\"保险\", \"培训\"], \"117\": [\"领导支持\", \"项目挑战\"], \"118\": \"自由回答 47\", \"119\": \"自由回答 48\", \"120\": \"一般\", \"121\": [\"奖金\"], \"122\": \"自由回答 27\"}',NULL,32,'财务部','senior'),(128,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"良好\", \"115\": \"很好\", \"116\": [\"薪资\", \"保险\"], \"117\": [\"领导支持\", \"学习机会\"], \"118\": \"自由回答 51\", \"119\": \"自由回答 48\", \"120\": \"一般\", \"121\": [\"奖金\", \"期权\"], \"122\": \"自由回答 7\"}',NULL,54,'技术部','executive'),(129,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"良好\", \"115\": \"较差\", \"116\": [\"培训\", \"薪资\"], \"117\": [\"晋升\", \"领导支持\"], \"118\": \"自由回答 90\", \"119\": \"自由回答 5\", \"120\": \"一般\", \"121\": [\"休假\"], \"122\": \"自由回答 17\"}',NULL,37,'市场部','senior'),(130,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"还行\", \"116\": [\"培训\"], \"117\": [\"晋升\"], \"118\": \"自由回答 7\", \"119\": \"自由回答 38\", \"120\": \"不认可\", \"121\": [\"休假\", \"表彰\"], \"122\": \"自由回答 23\"}',NULL,30,'运营部','junior'),(131,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"一般\", \"115\": \"还行\", \"116\": [\"培训\", \"保险\"], \"117\": [\"晋升\", \"学习机会\"], \"118\": \"自由回答 41\", \"119\": \"自由回答 17\", \"120\": \"一般\", \"121\": [\"期权\", \"奖金\"], \"122\": \"自由回答 29\"}',NULL,50,'市场部','executive'),(132,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"薪资\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 63\", \"119\": \"自由回答 5\", \"120\": \"不认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 7\"}',NULL,30,'产品部','intern'),(133,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"很好\", \"116\": [\"培训\", \"薪资\"], \"117\": [\"领导支持\", \"学习机会\"], \"118\": \"自由回答 1\", \"119\": \"自由回答 38\", \"120\": \"基本认可\", \"121\": [\"期权\"], \"122\": \"自由回答 86\"}',NULL,41,'技术部','senior'),(134,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"优秀\", \"115\": \"较差\", \"116\": [\"培训\"], \"117\": [\"晋升\", \"项目挑战\"], \"118\": \"自由回答 22\", \"119\": \"自由回答 99\", \"120\": \"不认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 73\"}',NULL,29,'人事部','intern'),(135,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"较差\", \"115\": \"一般\", \"116\": [\"薪资\"], \"117\": [\"晋升\"], \"118\": \"自由回答 30\", \"119\": \"自由回答 45\", \"120\": \"一般\", \"121\": [\"休假\", \"表彰\"], \"122\": \"自由回答 21\"}',NULL,33,'人事部','executive'),(136,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"良好\", \"115\": \"一般\", \"116\": [\"培训\"], \"117\": [\"领导支持\", \"晋升\"], \"118\": \"自由回答 88\", \"119\": \"自由回答 68\", \"120\": \"基本认可\", \"121\": [\"期权\"], \"122\": \"自由回答 36\"}',NULL,42,'产品部','senior'),(137,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"较差\", \"115\": \"一般\", \"116\": [\"培训\"], \"117\": [\"学习机会\", \"项目挑战\"], \"118\": \"自由回答 97\", \"119\": \"自由回答 14\", \"120\": \"基本认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 19\"}',NULL,31,'人事部','executive'),(138,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"一般\", \"115\": \"一般\", \"116\": [\"弹性工作\"], \"117\": [\"学习机会\", \"项目挑战\"], \"118\": \"自由回答 76\", \"119\": \"自由回答 37\", \"120\": \"一般\", \"121\": [\"期权\", \"表彰\"], \"122\": \"自由回答 85\"}',NULL,37,'市场部','manager'),(139,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"较差\", \"115\": \"还行\", \"116\": [\"培训\", \"薪资\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 85\", \"119\": \"自由回答 38\", \"120\": \"基本认可\", \"121\": [\"休假\"], \"122\": \"自由回答 9\"}',NULL,33,'人事部','executive'),(140,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"良好\", \"115\": \"很好\", \"116\": [\"培训\"], \"117\": [\"领导支持\", \"学习机会\"], \"118\": \"自由回答 65\", \"119\": \"自由回答 79\", \"120\": \"基本认可\", \"121\": [\"休假\"], \"122\": \"自由回答 46\"}',NULL,44,'运营部','executive'),(141,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"较差\", \"115\": \"还行\", \"116\": [\"薪资\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 26\", \"119\": \"自由回答 89\", \"120\": \"基本认可\", \"121\": [\"期权\", \"表彰\"], \"122\": \"自由回答 39\"}',NULL,41,'产品部','manager'),(142,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"良好\", \"115\": \"还行\", \"116\": [\"保险\", \"薪资\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 57\", \"119\": \"自由回答 67\", \"120\": \"基本认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 17\"}',NULL,41,'人事部','intern'),(143,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"一般\", \"115\": \"一般\", \"116\": [\"保险\"], \"117\": [\"项目挑战\", \"晋升\"], \"118\": \"自由回答 20\", \"119\": \"自由回答 45\", \"120\": \"一般\", \"121\": [\"表彰\"], \"122\": \"自由回答 96\"}',NULL,35,'市场部','junior'),(144,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"良好\", \"115\": \"一般\", \"116\": [\"保险\", \"培训\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 30\", \"119\": \"自由回答 5\", \"120\": \"一般\", \"121\": [\"休假\"], \"122\": \"自由回答 68\"}',NULL,38,'财务部','junior'),(145,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"保险\", \"薪资\"], \"117\": [\"晋升\", \"项目挑战\"], \"118\": \"自由回答 25\", \"119\": \"自由回答 11\", \"120\": \"基本认可\", \"121\": [\"奖金\"], \"122\": \"自由回答 70\"}',NULL,45,'技术部','intern'),(146,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"良好\", \"115\": \"较差\", \"116\": [\"保险\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 62\", \"119\": \"自由回答 12\", \"120\": \"认可\", \"121\": [\"期权\", \"奖金\"], \"122\": \"自由回答 9\"}',NULL,43,'运营部','executive'),(147,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"良好\", \"115\": \"一般\", \"116\": [\"弹性工作\", \"保险\"], \"117\": [\"领导支持\"], \"118\": \"自由回答 94\", \"119\": \"自由回答 86\", \"120\": \"不认可\", \"121\": [\"期权\", \"休假\"], \"122\": \"自由回答 68\"}',NULL,34,'财务部','junior'),(148,35,NULL,'2025-12-09 21:16:17','{\"113\": \"非常满意\", \"114\": \"优秀\", \"115\": \"一般\", \"116\": [\"弹性工作\"], \"117\": [\"学习机会\"], \"118\": \"自由回答 16\", \"119\": \"自由回答 43\", \"120\": \"认可\", \"121\": [\"休假\", \"表彰\"], \"122\": \"自由回答 54\"}',NULL,45,'财务部','intern'),(149,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"保险\", \"弹性工作\"], \"117\": [\"学习机会\", \"晋升\"], \"118\": \"自由回答 34\", \"119\": \"自由回答 100\", \"120\": \"认可\", \"121\": [\"休假\", \"奖金\"], \"122\": \"自由回答 82\"}',NULL,45,'技术部','manager'),(150,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"优秀\", \"115\": \"较差\", \"116\": [\"保险\", \"薪资\"], \"117\": [\"领导支持\", \"项目挑战\"], \"118\": \"自由回答 20\", \"119\": \"自由回答 64\", \"120\": \"认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 57\"}',NULL,44,'运营部','intern'),(151,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"培训\"], \"117\": [\"晋升\"], \"118\": \"自由回答 73\", \"119\": \"自由回答 36\", \"120\": \"认可\", \"121\": [\"期权\", \"奖金\"], \"122\": \"自由回答 36\"}',NULL,34,'市场部','intern'),(152,35,NULL,'2025-12-09 21:16:17','{\"113\": \"不满意\", \"114\": \"一般\", \"115\": \"较差\", \"116\": [\"弹性工作\", \"培训\"], \"117\": [\"晋升\", \"学习机会\"], \"118\": \"自由回答 32\", \"119\": \"自由回答 25\", \"120\": \"不认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 93\"}',NULL,29,'产品部','junior'),(153,35,NULL,'2025-12-09 21:16:17','{\"113\": \"一般\", \"114\": \"良好\", \"115\": \"较差\", \"116\": [\"保险\", \"培训\"], \"117\": [\"项目挑战\", \"领导支持\"], \"118\": \"自由回答 78\", \"119\": \"自由回答 59\", \"120\": \"一般\", \"121\": [\"休假\"], \"122\": \"自由回答 94\"}',NULL,34,'运营部','executive'),(154,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"较差\", \"115\": \"还行\", \"116\": [\"培训\", \"薪资\"], \"117\": [\"晋升\", \"领导支持\"], \"118\": \"自由回答 71\", \"119\": \"自由回答 60\", \"120\": \"不认可\", \"121\": [\"表彰\"], \"122\": \"自由回答 73\"}',NULL,36,'人事部','senior'),(155,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"较差\", \"115\": \"一般\", \"116\": [\"薪资\"], \"117\": [\"项目挑战\"], \"118\": \"自由回答 76\", \"119\": \"自由回答 21\", \"120\": \"基本认可\", \"121\": [\"表彰\", \"奖金\"], \"122\": \"自由回答 82\"}',NULL,36,'市场部','executive'),(156,35,NULL,'2025-12-09 21:16:17','{\"113\": \"满意\", \"114\": \"较差\", \"115\": \"一般\", \"116\": [\"弹性工作\"], \"117\": [\"项目挑战\", \"学习机会\"], \"118\": \"自由回答 95\", \"119\": \"自由回答 24\", \"120\": \"基本认可\", \"121\": [\"表彰\", \"奖金\"], \"122\": \"自由回答 51\"}',NULL,38,'市场部','senior');
/*!40000 ALTER TABLE `survey_answers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `survey_questions`
--

DROP TABLE IF EXISTS `survey_questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `survey_questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `survey_id` int NOT NULL,
  `question_id` int NOT NULL,
  `order` int NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `survey_id` (`survey_id`),
  KEY `question_id` (`question_id`),
  KEY `ix_survey_questions_id` (`id`),
  CONSTRAINT `survey_questions_ibfk_1` FOREIGN KEY (`survey_id`) REFERENCES `surveys` (`id`),
  CONSTRAINT `survey_questions_ibfk_2` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=93 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `survey_questions`
--

LOCK TABLES `survey_questions` WRITE;
/*!40000 ALTER TABLE `survey_questions` DISABLE KEYS */;
INSERT INTO `survey_questions` VALUES (67,30,74,1,'2025-12-07 12:40:50'),(68,30,75,2,'2025-12-07 12:40:50'),(69,30,76,3,'2025-12-07 12:40:50'),(70,29,74,1,'2025-12-07 12:43:42'),(71,29,75,2,'2025-12-07 12:43:42'),(72,29,76,3,'2025-12-07 12:43:42'),(83,35,113,1,'2025-12-09 13:16:17'),(84,35,114,2,'2025-12-09 13:16:17'),(85,35,115,3,'2025-12-09 13:16:17'),(86,35,116,4,'2025-12-09 13:16:17'),(87,35,117,5,'2025-12-09 13:16:17'),(88,35,118,6,'2025-12-09 13:16:17'),(89,35,119,7,'2025-12-09 13:16:17'),(90,35,120,8,'2025-12-09 13:16:17'),(91,35,121,9,'2025-12-09 13:16:17'),(92,35,122,10,'2025-12-09 13:16:17');
/*!40000 ALTER TABLE `survey_questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `surveys`
--

DROP TABLE IF EXISTS `surveys`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `surveys` (
  `id` int NOT NULL AUTO_INCREMENT,
  `title` varchar(255) NOT NULL,
  `description` text,
  `created_by_user_id` int NOT NULL,
  `created_at` datetime DEFAULT (now()),
  `updated_at` datetime DEFAULT NULL,
  `organization_id` int DEFAULT NULL,
  `status` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `created_by_user_id` (`created_by_user_id`),
  KEY `ix_surveys_id` (`id`),
  KEY `ix_surveys_title` (`title`),
  KEY `organization_id` (`organization_id`),
  CONSTRAINT `surveys_ibfk_1` FOREIGN KEY (`created_by_user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `surveys_ibfk_2` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `surveys`
--

LOCK TABLES `surveys` WRITE;
/*!40000 ALTER TABLE `surveys` DISABLE KEYS */;
INSERT INTO `surveys` VALUES (22,'员工满意度调研','员工满意度调研',3,'2025-08-22 04:12:18','2025-08-22 04:12:18',13,'pending'),(23,'员工满意度调研','员工满意度调研',3,'2025-08-22 04:12:18','2025-08-22 04:12:18',14,'pending'),(24,'员工满意度调研','员工满意度调研',3,'2025-08-22 04:12:18','2025-08-22 04:12:18',15,'pending'),(25,'员工满意度调研','员工满意度调研',3,'2025-08-22 04:12:18','2025-08-22 04:12:18',16,'pending'),(26,'测试1','',6,'2025-08-27 15:30:36','2025-08-27 15:30:36',NULL,'pending'),(29,'调研2','',2,'2025-12-06 07:58:10','2025-12-06 07:58:10',NULL,'pending'),(30,'调研3','',2,'2025-12-06 08:46:27','2025-12-06 08:46:27',NULL,'pending'),(35,'模拟问卷 - 部门职务测试','模拟数据问卷，用于图表与分析测试',2,'2025-12-09 13:16:17','2025-12-09 13:16:17',NULL,'pending');
/*!40000 ALTER TABLE `surveys` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `color` varchar(20) DEFAULT '#409EFF',
  `description` text,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_tag_name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (1,'员工福利','#67C23A','关于员工福利、薪资、保险等方面的问题','2025-08-27 14:56:29','2025-08-27 14:56:29'),(2,'工作环境','#E6A23C','关于工作环境、办公条件、设施等方面的问题','2025-08-27 14:56:29','2025-08-27 14:56:29'),(3,'团队协作','#409EFF','关于团队合作、沟通、协作等方面的问题','2025-08-27 14:56:29','2025-08-27 14:56:29'),(4,'领导力','#F56C6C','关于领导能力、管理风格、决策等方面的问题','2025-08-27 14:56:29','2025-08-27 14:56:29'),(5,'职业发展','#909399','关于职业规划、培训、晋升等方面的问题','2025-08-27 14:56:29','2025-08-27 14:56:29'),(6,'公司文化','#9C27B0','关于企业文化、价值观、氛围等方面的问题','2025-08-27 14:56:29','2025-08-27 14:56:29'),(7,'工作满意度','#FF9800','关于工作满意度、工作体验等方面的问题','2025-08-27 14:56:29','2025-08-27 14:56:29'),(8,'创新思维','#4CAF50','关于创新、创意、改进建议等方面的问题','2025-08-27 14:56:29','2025-08-27 14:56:29'),(9,'测试标签1','#409EFF',NULL,'2025-12-08 13:20:27','2025-12-08 13:20:27');
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `organization_id` int DEFAULT NULL,
  `manager_id` int DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`),
  KEY `organization_id` (`organization_id`),
  KEY `ix_users_id` (`id`),
  KEY `manager_id` (`manager_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`organization_id`) REFERENCES `organizations` (`id`),
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`manager_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'string','user@example.com','$2b$12$8RDQlVmzKyBgK0j5OSmKkOdrTZ.Yeo0XvcBCLvOJ7yvKZ6BUWnf6i','employee','2025-07-31 03:24:46','2025-08-17 16:14:16',NULL,NULL,1),(2,'CaibiJuhao','he2827987@gmail.com','$2b$12$92EfNFmql91ZKG.AyD6EluvULHOBzd8JL4Kflo2W6E9V.dNLC32B2','employee','2025-07-31 03:43:49','2025-08-23 03:52:49',NULL,NULL,1),(3,'admin','admin@example.com','$2b$12$kSAScQDPa3ZgjD/GTBmk1eSr0Li1fxVmaFrdcNPLbqJGxF0hKzYee','employee','2025-08-16 06:43:32','2025-08-17 16:14:16',NULL,NULL,1),(4,'testuser_1756307744','testuser_1756307744@example.com','$2b$12$esd984mnLTCiR.Laosu/2Oi4LqFVuncL2aXj0FxOkRRlXPx1j9jva','employee','2025-08-27 15:15:45','2025-08-27 15:15:45',NULL,NULL,1),(5,'testuser_1756307766','testuser_1756307766@example.com','$2b$12$45GgNoPjWyWSHtMn3O41SO/ZpCyFKx2m5eE.wUJo3iDekz3R9uXl6','employee','2025-08-27 15:16:07','2025-08-27 15:16:07',NULL,NULL,1),(6,'testuser','testuser@example.com','$2b$12$4Wr7gZTvQCJbOV8pzXKINe1VYmWmMlZh56EM9hFI40tk/fa7R6EkK','employee','2025-08-27 15:17:11','2025-08-27 15:17:11',NULL,NULL,1),(7,'frontend_user_1756307833','frontend_user_1756307833@example.com','$2b$12$AEg3O.2koR/6eSspPhTGcOhZSJjdyBvelzX9fTHj/tIL/VDU/FzjO','employee','2025-08-27 15:17:13','2025-08-27 15:17:13',NULL,NULL,1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-11 21:45:21
