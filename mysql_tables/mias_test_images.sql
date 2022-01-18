-- MySQL dump 10.13  Distrib 8.0.21, for Win64 (x86_64)
--
-- Host: localhost    Database: mias
-- ------------------------------------------------------
-- Server version	8.0.21

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `test_images`
--

DROP TABLE IF EXISTS `test_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `test_images` (
  `id` int NOT NULL AUTO_INCREMENT,
  `test_image_id` varchar(255) NOT NULL,
  `uploader_id` int NOT NULL,
  `img_type` varchar(700) DEFAULT NULL,
  `img_path` varchar(500) DEFAULT NULL,
  `acquired_date` date DEFAULT NULL,
  `examination_source` varchar(45) DEFAULT NULL,
  `acquired_body_part` varchar(45) DEFAULT NULL,
  `description` varchar(500) DEFAULT NULL,
  PRIMARY KEY (`id`,`test_image_id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `test_image_id_UNIQUE` (`test_image_id`)
) ENGINE=InnoDB AUTO_INCREMENT=90 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_images`
--

LOCK TABLES `test_images` WRITE;
/*!40000 ALTER TABLE `test_images` DISABLE KEYS */;
INSERT INTO `test_images` VALUES (62,'ti001',484,'Normal Image','D:/Projects/MIAS_Project/mias/media/484_1589360791/','2020-05-05','Test',NULL,''),(63,'ti002',484,'Normal Image','D:/Projects/MIAS_Project/mias/media/484_1589360839/','2020-05-02','Hospital',NULL,''),(64,'ti003',484,'Normal Image','D:/Projects/MIAS_Project/mias/media/484_1589360858/','2020-05-10','Hospital',NULL,''),(65,'ti004',484,'CT','D:/Projects/MIAS_Project/mias/media/484_1589360898/','2020-05-09','Hospital',NULL,''),(66,'ti005',484,'CT','D:/Projects/MIAS_Project/mias/media/484_1589434770/','2020-05-05','Test',NULL,''),(67,'ti006',484,'Normal Image','D:/Projects/MIAS_Project/mias/media/484_1589440746/','2020-05-14','Test',NULL,''),(88,'ti999',1,'CT','E:','2020-07-11','temp','liver','temp');
/*!40000 ALTER TABLE `test_images` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-01-18 21:36:32
