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
-- Table structure for table `diagnosis_liver`
--

DROP TABLE IF EXISTS `diagnosis_liver`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnosis_liver` (
  `pat_name` varchar(50) NOT NULL,
  `mrn` varchar(45) NOT NULL,
  `img_id` varchar(200) NOT NULL,
  `tumor_types` varchar(100) NOT NULL,
  `aphe_types` varchar(45) NOT NULL,
  `tumor_sizes` varchar(45) NOT NULL,
  `num_mfs` varchar(45) NOT NULL,
  `stages` varchar(45) NOT NULL,
  `diagnosis_id` int NOT NULL AUTO_INCREMENT,
  `birthday` varchar(45) NOT NULL,
  `diagnosis_date` varchar(100) NOT NULL,
  PRIMARY KEY (`diagnosis_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diagnosis_liver`
--

LOCK TABLES `diagnosis_liver` WRITE;
/*!40000 ALTER TABLE `diagnosis_liver` DISABLE KEYS */;
INSERT INTO `diagnosis_liver` VALUES ('test','test','test','test','test','test','test','test',1,'test','01-06-2022'),('John Johns','7159233','E:\\1. Lab\\Projects\\Medical Image Analytics System\\mias_with_lirads\\mias\\medical_image\\7159233','HCC','Nonrim','46.941 mm','1','LR-5',3,'18/07/1991','01-06-2022');
/*!40000 ALTER TABLE `diagnosis_liver` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-01-18 21:36:31
