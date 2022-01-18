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
-- Table structure for table `diagnosis`
--

DROP TABLE IF EXISTS `diagnosis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnosis` (
  `id` int NOT NULL AUTO_INCREMENT,
  `diagnosis_id` varchar(255) NOT NULL,
  `diagnosis_date` date NOT NULL,
  `description` varchar(255) NOT NULL,
  `symptom_id` int DEFAULT NULL,
  `medical_image_id` int DEFAULT NULL,
  `physician_id` int DEFAULT NULL,
  `patient_id` int DEFAULT NULL,
  `ml_model_id` int DEFAULT NULL,
  PRIMARY KEY (`id`,`diagnosis_id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `diagnosis_id_UNIQUE` (`diagnosis_id`),
  KEY `fk_test_table_images_diagnosis_idx` (`medical_image_id`),
  KEY `fk_symptom_diagnosis_idx` (`symptom_id`),
  CONSTRAINT `fk_symptom_diagnosis` FOREIGN KEY (`symptom_id`) REFERENCES `symptom` (`id`),
  CONSTRAINT `fk_test_images_diagnosis` FOREIGN KEY (`medical_image_id`) REFERENCES `test_images` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diagnosis`
--

LOCK TABLES `diagnosis` WRITE;
/*!40000 ALTER TABLE `diagnosis` DISABLE KEYS */;
INSERT INTO `diagnosis` VALUES (1,'dia001','2020-07-07','HCC possible',1,63,1,NULL,NULL),(11,'dia011','2020-01-01','high stress',1,64,1,NULL,NULL),(12,'dia012','2020-01-01','bad cold',1,65,1,NULL,NULL),(13,'dia013','2020-01-01','cancer',1,66,1,NULL,NULL),(16,'dia016','2020-01-01','HCC possible',1,67,1,NULL,NULL),(17,'dia017','2020-01-01','Risk of cirrhosis',1,67,1,NULL,NULL),(29,'dia029','2020-07-10','temp',1,67,1,1,1);
/*!40000 ALTER TABLE `diagnosis` ENABLE KEYS */;
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
