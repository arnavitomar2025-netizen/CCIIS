-- MySQL dump 10.13  Distrib 9.7.1, for macos15 (arm64)
--
-- Host: localhost    Database: project_cciis
-- ------------------------------------------------------
-- Server version	9.7.1

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
-- Table structure for table `ncrp_analytical_report`
--

DROP TABLE IF EXISTS `ncrp_analytical_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncrp_analytical_report` (
  `report_id` varchar(36) NOT NULL,
  `author_id` varchar(36) NOT NULL,
  `rep_type` varchar(50) NOT NULL,
  `generated_dt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `is_admissible` tinyint(1) DEFAULT '1',
  `doc_summary` text NOT NULL,
  `doc_no` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`report_id`),
  KEY `fk_report_author` (`author_id`),
  KEY `fk_report_docket` (`doc_no`),
  CONSTRAINT `fk_report_author` FOREIGN KEY (`author_id`) REFERENCES `NCRP_REGISTRANT_PROFILE` (`reg_id`),
  CONSTRAINT `fk_report_docket` FOREIGN KEY (`doc_no`) REFERENCES `ncrp_incident_docket` (`doc_no`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ncrp_analytical_report`
--

LOCK TABLES `ncrp_analytical_report` WRITE;
/*!40000 ALTER TABLE `ncrp_analytical_report` DISABLE KEYS */;
INSERT INTO `ncrp_analytical_report` VALUES ('rep-001','reg-003','LINK_ANALYSIS','2026-10-08 18:30:48',1,'Two dockets share IP 103.21.44.9','NCRP/2026/0001'),('rep-002','reg-003','FINANCIAL_TRACE','2026-10-08 18:30:48',1,'Funds routed via mule account','NCRP/2026/0002'),('REP-UUID-001','USR-UUID-107','CRIME_STATS','2026-09-10 17:07:17',1,'Quarterly analysis indicates a 15% rise in UPI collectible frauds targeting urban centers.',NULL),('REP-UUID-002','USR-UUID-108','MODUS_OPERANDI','2026-09-10 17:07:17',1,'Analysis of phishing domains reveals common hosting infrastructure across multiple credential harvesting campaigns.',NULL),('REP-UUID-003','USR-UUID-109','FINANCIAL_FLOW','2026-09-10 17:07:17',1,'Tracing mule bank accounts linked to investment syndicates across 4 state jurisdictions.',NULL),('REP-UUID-004','USR-UUID-110','THREAT_INTEL','2026-09-10 17:07:17',1,'Ransomware deployment indicators matching known APT actor behavior patterns.',NULL),('REP-UUID-005','USR-UUID-111','ADMIN_SUMMARY','2026-09-10 17:07:17',0,'Internal resource allocation audit for cyber cell division personnel.',NULL),('REP-UUID-006','USR-UUID-107','TREND_ANALYSIS','2026-09-10 17:07:17',1,'Spike in simulated task-based social media scams during festive seasons.',NULL),('REP-UUID-007','USR-UUID-108','FORENSIC_SUMMARY','2026-09-10 17:07:17',1,'Summary of cryptographic hash evaluations for seized digital media evidence items.',NULL),('REP-UUID-008','USR-UUID-109','NETWORK_MAPPING','2026-09-10 17:07:17',1,'Mapping of IP address nodes utilized in SIM swapping rings across metropolitan areas.',NULL),('REP-UUID-009','USR-UUID-110','RECOVERY_REPORT','2026-09-10 17:07:17',1,'Analysis of successful fund freezes and chargeback reversals coordinated with banking ombudsmen.',NULL),('REP-UUID-010','USR-UUID-112','STRATEGIC_BRIEF','2026-09-10 17:07:17',1,'High-level executive overview of state cybercrime prevention policies and public awareness metrics.',NULL);
/*!40000 ALTER TABLE `ncrp_analytical_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ncrp_audit_log`
--

DROP TABLE IF EXISTS `ncrp_audit_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncrp_audit_log` (
  `log_id` bigint NOT NULL AUTO_INCREMENT,
  `table_name` varchar(50) NOT NULL,
  `action` varchar(20) NOT NULL,
  `record_key` varchar(60) NOT NULL,
  `old_value` varchar(255) DEFAULT NULL,
  `new_value` varchar(255) DEFAULT NULL,
  `changed_by` varchar(100) DEFAULT NULL,
  `changed_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ncrp_audit_log`
--

LOCK TABLES `ncrp_audit_log` WRITE;
/*!40000 ALTER TABLE `ncrp_audit_log` DISABLE KEYS */;
INSERT INTO `ncrp_audit_log` VALUES (1,'ncrp_forensic_evidence','INSERT','ev-001',NULL,'NCRP/2026/0001 | phish_email.eml','root@localhost','2026-10-08 18:30:44'),(2,'ncrp_forensic_evidence','INSERT','ev-002',NULL,'NCRP/2026/0001 | call_log.pdf','root@localhost','2026-10-08 18:30:44'),(3,'ncrp_forensic_evidence','INSERT','ev-003',NULL,'NCRP/2026/0002 | wallet_txn.csv','root@localhost','2026-10-08 18:30:44'),(4,'ncrp_incident_docket','STAGE_CHANGE','NCRP/2026/0003','TRIAGE','INVESTIGATION','root@localhost','2026-10-08 18:35:21');
/*!40000 ALTER TABLE `ncrp_audit_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ncrp_docket_pattern_link`
--

DROP TABLE IF EXISTS `ncrp_docket_pattern_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncrp_docket_pattern_link` (
  `doc_no` varchar(30) NOT NULL,
  `cluster_id` varchar(36) NOT NULL,
  `matched_dt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`doc_no`,`cluster_id`),
  KEY `idx_dp_cluster` (`cluster_id`),
  CONSTRAINT `fk_dp_cluster` FOREIGN KEY (`cluster_id`) REFERENCES `NCRP_PATTERN_CLUSTER` (`cluster_id`),
  CONSTRAINT `fk_dp_docket` FOREIGN KEY (`doc_no`) REFERENCES `NCRP_INCIDENT_DOCKET` (`doc_no`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ncrp_docket_pattern_link`
--

LOCK TABLES `ncrp_docket_pattern_link` WRITE;
/*!40000 ALTER TABLE `ncrp_docket_pattern_link` DISABLE KEYS */;
INSERT INTO `ncrp_docket_pattern_link` VALUES ('CYBER-20260901-1001','CLST-UUID-001','2026-09-10 17:06:59'),('CYBER-20260901-1001','CLST-UUID-002','2026-09-10 17:06:59'),('CYBER-20260902-1002','CLST-UUID-003','2026-09-10 17:06:59'),('CYBER-20260903-1003','CLST-UUID-006','2026-09-10 17:06:59'),('CYBER-20260903-1004','CLST-UUID-008','2026-09-10 17:06:59'),('CYBER-20260904-1005','CLST-UUID-004','2026-09-10 17:06:59'),('CYBER-20260905-1006','CLST-UUID-005','2026-09-10 17:06:59'),('CYBER-20260906-1007','CLST-UUID-007','2026-09-10 17:06:59'),('CYBER-20260907-1008','CLST-UUID-005','2026-09-10 17:06:59'),('CYBER-20260908-1009','CLST-UUID-001','2026-09-10 17:06:59'),('CYBER-20260909-1010','CLST-UUID-009','2026-09-10 17:06:59'),('NCRP/2026/0001','cl-001','2026-10-08 18:30:44'),('NCRP/2026/0002','cl-002','2026-10-08 18:30:44'),('NCRP/2026/0003','cl-001','2026-10-08 18:30:44');
/*!40000 ALTER TABLE `ncrp_docket_pattern_link` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_pattern_link_after_insert` AFTER INSERT ON `ncrp_docket_pattern_link` FOR EACH ROW BEGIN
  UPDATE ncrp_pattern_cluster
  SET risk_score = LEAST(100, IFNULL(risk_score,0) + 5)
  WHERE cluster_id = NEW.cluster_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `ncrp_docket_suspect_link`
--

DROP TABLE IF EXISTS `ncrp_docket_suspect_link`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncrp_docket_suspect_link` (
  `doc_no` varchar(30) NOT NULL,
  `suspect_id` bigint NOT NULL,
  `linked_dt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `conf_score` decimal(3,2) DEFAULT '1.00',
  PRIMARY KEY (`doc_no`,`suspect_id`),
  KEY `idx_ds_suspect` (`suspect_id`),
  CONSTRAINT `fk_ds_docket` FOREIGN KEY (`doc_no`) REFERENCES `NCRP_INCIDENT_DOCKET` (`doc_no`),
  CONSTRAINT `fk_ds_suspect` FOREIGN KEY (`suspect_id`) REFERENCES `NCRP_SUSPECT_ENTITY` (`suspect_id`),
  CONSTRAINT `chk_conf` CHECK ((`conf_score` between 0 and 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ncrp_docket_suspect_link`
--

LOCK TABLES `ncrp_docket_suspect_link` WRITE;
/*!40000 ALTER TABLE `ncrp_docket_suspect_link` DISABLE KEYS */;
INSERT INTO `ncrp_docket_suspect_link` VALUES ('CYBER-20260901-1001',1,'2026-09-10 17:04:46',0.95),('CYBER-20260901-1001',2,'2026-09-10 17:04:46',0.65),('CYBER-20260902-1002',2,'2026-09-10 17:04:46',0.88),('CYBER-20260903-1003',10,'2026-09-10 17:04:46',0.92),('CYBER-20260903-1004',9,'2026-09-10 17:04:46',0.85),('CYBER-20260904-1005',3,'2026-09-10 17:04:46',0.96),('CYBER-20260905-1006',5,'2026-09-10 17:04:46',0.79),('CYBER-20260906-1007',7,'2026-09-10 17:04:46',0.99),('CYBER-20260907-1008',8,'2026-09-10 17:04:46',0.91),('CYBER-20260908-1009',6,'2026-09-10 17:04:46',0.94),('CYBER-20260909-1010',4,'2026-09-10 17:04:46',0.87),('CYBER-20260910-9999',1,'2026-09-10 17:16:06',0.90),('NCRP/2026/0001',1,'2026-10-08 18:30:44',0.90),('NCRP/2026/0002',2,'2026-10-08 18:30:44',0.95),('NCRP/2026/0003',1,'2026-10-08 18:30:44',0.40),('NCRP/2026/0003',3,'2026-10-08 18:30:44',0.75),('NCRP/2026/0004',1,'2026-10-08 18:30:44',0.60);
/*!40000 ALTER TABLE `ncrp_docket_suspect_link` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ncrp_forensic_evidence`
--

DROP TABLE IF EXISTS `ncrp_forensic_evidence`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncrp_forensic_evidence` (
  `evidence_id` varchar(40) NOT NULL,
  `doc_no` varchar(30) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_type` varchar(80) NOT NULL,
  `file_path` varchar(500) NOT NULL,
  `sha_hash` char(64) NOT NULL,
  `uploaded_dt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `uploader_id` varchar(36) NOT NULL,
  PRIMARY KEY (`evidence_id`),
  KEY `fk_evid_docket` (`doc_no`),
  KEY `fk_evid_uploader` (`uploader_id`),
  CONSTRAINT `fk_evid_docket` FOREIGN KEY (`doc_no`) REFERENCES `ncrp_incident_docket` (`doc_no`) ON DELETE CASCADE,
  CONSTRAINT `fk_evid_uploader` FOREIGN KEY (`uploader_id`) REFERENCES `ncrp_registrant_profile` (`reg_id`),
  CONSTRAINT `fk_evidence_docket` FOREIGN KEY (`doc_no`) REFERENCES `NCRP_INCIDENT_DOCKET` (`doc_no`),
  CONSTRAINT `fk_evidence_uploader` FOREIGN KEY (`uploader_id`) REFERENCES `NCRP_REGISTRANT_PROFILE` (`reg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ncrp_forensic_evidence`
--

LOCK TABLES `ncrp_forensic_evidence` WRITE;
/*!40000 ALTER TABLE `ncrp_forensic_evidence` DISABLE KEYS */;
INSERT INTO `ncrp_forensic_evidence` VALUES ('ev-001','NCRP/2026/0001','phish_email.eml','message/rfc822','/evidence/0001/phish_email.eml','437365e06e13db15193002490de0368491573d5031618f58ee76122a476020fd','2026-10-08 18:30:44','reg-002'),('ev-002','NCRP/2026/0001','call_log.pdf','application/pdf','/evidence/0001/call_log.pdf','ae853bf25e2001529385ece1c429f59996d688521d1abcf7afe29aaf2b516af0','2026-10-08 18:30:44','reg-002'),('ev-003','NCRP/2026/0002','wallet_txn.csv','text/csv','/evidence/0002/wallet_txn.csv','a9668032dd0ab3286ee1382e0f19e9426d18a2d884b1a4264dffd12866a310bc','2026-10-08 18:30:44','reg-003'),('EVID-UUID-001','CYBER-20260901-1001','screenshot_upi.png','image/png','/secure/evidence/2026/09/screenshot_upi.png','ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad','2026-09-10 17:06:06','USR-UUID-107'),('EVID-UUID-002','CYBER-20260902-1002','phishing_sms.pdf','application/pdf','/secure/evidence/2026/09/phishing_sms.pdf','fe507c64cff47926b429d2b27db86da5a9010bc13a693c9d1c0ff6058e38ea82','2026-09-10 17:06:06','USR-UUID-107'),('EVID-UUID-003','CYBER-20260903-1003','bank_statement.pdf','application/pdf','/secure/evidence/2026/09/bank_statement.pdf','9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08','2026-09-10 17:06:06','USR-UUID-108'),('EVID-UUID-004','CYBER-20260903-1004','chat_transcript.txt','text/plain','/secure/evidence/2026/09/chat_transcript.txt','cf23df2207d99a74fbe169e3eba035e633b65d94760c762b9ae85359735d4834','2026-09-10 17:06:06','USR-UUID-108'),('EVID-UUID-005','CYBER-20260904-1005','crypto_receipt.png','image/png','/secure/evidence/2026/09/crypto_receipt.png','5d41402abc4b2a76b9719d911017c5922143736531383737a78a8348c08172c2','2026-09-10 17:06:06','USR-UUID-109'),('EVID-UUID-006','CYBER-20260905-1006','pan_card_copy.pdf','application/pdf','/secure/evidence/2026/09/pan_card_copy.pdf','7d793037a076018657b49293f0f35905d53955c423e20e8efc91c305c742c31e','2026-09-10 17:06:06','USR-UUID-109'),('EVID-UUID-007','CYBER-20260906-1007','ransom_note.txt','text/plain','/secure/evidence/2026/09/ransom_note.txt','6e75b31520330f81d1d8ef3f9909247eb9548455502c3b88950da5f81015c92c','2026-09-10 17:06:06','USR-UUID-110'),('EVID-UUID-008','CYBER-20260907-1008','profile_screenshot.jpg','image/jpeg','/secure/evidence/2026/09/profile_screenshot.jpg','2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824','2026-09-10 17:06:06','USR-UUID-110'),('EVID-UUID-009','CYBER-20260908-1009','telecom_log.csv','text/csv','/secure/evidence/2026/09/telecom_log.csv','486ea46224d1bb4fb680f34f7c9ad96a8f24ec88be73ea8e5a6c65263e9bdfa4','2026-09-10 17:06:06','USR-UUID-107'),('EVID-UUID-010','CYBER-20260909-1010','harassment_audio.mp3','audio/mpeg','/secure/evidence/2026/09/harassment_audio.mp3','b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9','2026-09-10 17:06:06','USR-UUID-108');
/*!40000 ALTER TABLE `ncrp_forensic_evidence` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_evidence_after_insert` AFTER INSERT ON `ncrp_forensic_evidence` FOR EACH ROW BEGIN
  INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
  VALUES ('ncrp_forensic_evidence', 'INSERT', NEW.evidence_id, NULL, CONCAT(NEW.doc_no,' | ',NEW.file_name), USER());
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `ncrp_incident_docket`
--

DROP TABLE IF EXISTS `ncrp_incident_docket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncrp_incident_docket` (
  `doc_no` varchar(30) NOT NULL,
  `victim_id` varchar(36) DEFAULT NULL,
  `officer_id` varchar(36) DEFAULT NULL,
  `event_dt` timestamp NOT NULL,
  `filed_dt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `crime_type` varchar(50) NOT NULL,
  `details` text NOT NULL,
  `stage_code` varchar(30) DEFAULT 'LOGGED',
  `loss_amt` decimal(12,2) DEFAULT '0.00',
  PRIMARY KEY (`doc_no`),
  KEY `fk_incident_victim` (`victim_id`),
  KEY `fk_incident_officer` (`officer_id`),
  KEY `idx_docket_stage` (`stage_code`),
  KEY `idx_docket_crime` (`crime_type`),
  KEY `idx_docket_filed` (`filed_dt`),
  CONSTRAINT `fk_incident_officer` FOREIGN KEY (`officer_id`) REFERENCES `NCRP_REGISTRANT_PROFILE` (`reg_id`),
  CONSTRAINT `fk_incident_victim` FOREIGN KEY (`victim_id`) REFERENCES `NCRP_REGISTRANT_PROFILE` (`reg_id`),
  CONSTRAINT `chk_loss_nonneg` CHECK ((`loss_amt` >= 0)),
  CONSTRAINT `chk_stage` CHECK ((`stage_code` in (_utf8mb4'TRIAGE',_utf8mb4'LOGGED',_utf8mb4'INVESTIGATION',_utf8mb4'CLOSED')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ncrp_incident_docket`
--

LOCK TABLES `ncrp_incident_docket` WRITE;
/*!40000 ALTER TABLE `ncrp_incident_docket` DISABLE KEYS */;
INSERT INTO `ncrp_incident_docket` VALUES ('CYBER-20260901-1001','USR-UUID-101','USR-UUID-107','2026-08-30 09:00:00','2026-09-10 17:03:45','UPI_FRAUD','Unauthorized debit via fake collect request claiming electricity bill payment.','TRIAGE',27500.00),('CYBER-20260902-1002','USR-UUID-102','USR-UUID-107','2026-09-01 04:45:00','2026-09-10 17:03:45','PHISHING','Victim received SMS link impersonating bank KYC update and entered credentials.','LOGGED',85000.50),('CYBER-20260903-1003','USR-UUID-103','USR-UUID-108','2026-09-02 03:30:00','2026-09-10 17:03:45','CREDIT_CARD_FRAUD','International unauthorized transactions made on e-commerce portal.','INVESTIGATION',45000.00),('CYBER-20260903-1004','USR-UUID-104','USR-UUID-108','2026-09-02 12:50:00','2026-09-10 17:03:45','JOB_FRAUD','Part-time YouTube liking job task scam resulting in payment extortion.','TRIAGE',12000.00),('CYBER-20260904-1005','USR-UUID-105','USR-UUID-109','2026-09-03 06:15:00','2026-09-10 17:03:45','INVESTMENT_SCAM','Telegram group promising high returns on crypto trading platform.','INVESTIGATION',250000.00),('CYBER-20260905-1006','USR-UUID-106','USR-UUID-109','2026-09-04 10:40:00','2026-09-10 17:03:45','IDENTITY_THEFT','Stolen PAN details used to issue micro-loans on digital lending apps.','CLOSED',60000.00),('CYBER-20260906-1007','USR-UUID-101','USR-UUID-110','2026-09-05 03:00:00','2026-09-10 17:03:45','RANSOMWARE','Corporate workstation encrypted; ransom demanded in Monero.','LOGGED',500000.00),('CYBER-20260907-1008','USR-UUID-102','USR-UUID-110','2026-09-06 06:30:00','2026-09-10 17:03:45','SOCIAL_MEDIA_HACK','Instagram account compromised and used to solicit money from contacts.','TRIAGE',5000.00),('CYBER-20260908-1009','USR-UUID-103','USR-UUID-107','2026-09-07 14:10:00','2026-09-10 17:03:45','SIM_SWAP','Cellular service disconnected followed by unauthorized bank OTP intercepts.','INVESTIGATION',135000.00),('CYBER-20260909-1010','USR-UUID-104','USR-UUID-108','2026-09-08 09:55:00','2026-09-10 17:03:45','LOAN_APP_HARASSMENT','Abusive calls received from illegal loan application recovery agents.','CLOSED',15000.00),('CYBER-20260910-1003','USR-UUID-101','USR-UUID-107','2026-09-10 17:09:27','2026-09-10 17:09:27','IDENTITY_THEFT','Unauthorized loan application filed using stolen KYC docs.','LOGGED',150000.00),('CYBER-20260910-9999','USR-UUID-102',NULL,'2026-09-10 17:16:06','2026-09-10 17:16:06','PHISHING','Simulated transaction test.','LOGGED',1200.00),('NCRP/2026/0001','reg-004','reg-002','2026-09-01 05:00:00','2026-10-08 18:30:44','Phishing','Fake bank KYC link','INVESTIGATION',45000.00),('NCRP/2026/0002','reg-005','reg-002','2026-09-03 08:30:00','2026-10-08 18:30:44','Investment Fraud','Crypto scheme','INVESTIGATION',250000.00),('NCRP/2026/0003','reg-004','reg-002','2026-09-10 03:45:00','2026-10-08 18:30:44','UPI Fraud','QR refund scam','INVESTIGATION',12000.00),('NCRP/2026/0004','reg-005','reg-002','2026-09-15 13:15:00','2026-10-08 18:30:44','Phishing','SMS link fraud','CLOSED',8000.00),('NCRP/2026/0005','reg-004','reg-002','2026-09-20 05:30:00','2026-10-08 18:30:44','Identity Theft','Aadhaar misuse','LOGGED',0.00);
/*!40000 ALTER TABLE `ncrp_incident_docket` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_audit_loss_update` BEFORE UPDATE ON `ncrp_incident_docket` FOR EACH ROW BEGIN
    IF NEW.loss_amt < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Loss amount cannot be negative.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_docket_before_update` BEFORE UPDATE ON `ncrp_incident_docket` FOR EACH ROW BEGIN
  IF OLD.stage_code = 'CLOSED' AND NEW.stage_code <> 'CLOSED' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Closed dockets cannot be reopened';
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_docket_after_update` AFTER UPDATE ON `ncrp_incident_docket` FOR EACH ROW BEGIN
  IF OLD.stage_code <> NEW.stage_code THEN
    INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
    VALUES ('ncrp_incident_docket', 'STAGE_CHANGE', OLD.doc_no, OLD.stage_code, NEW.stage_code, USER());
  END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_docket_after_delete` AFTER DELETE ON `ncrp_incident_docket` FOR EACH ROW BEGIN
  INSERT INTO ncrp_audit_log (table_name, action, record_key, old_value, new_value, changed_by)
  VALUES ('ncrp_incident_docket', 'DELETE', OLD.doc_no, OLD.crime_type, NULL, USER());
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `ncrp_pattern_cluster`
--

DROP TABLE IF EXISTS `ncrp_pattern_cluster`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncrp_pattern_cluster` (
  `cluster_id` varchar(36) NOT NULL,
  `pattern_type` varchar(40) NOT NULL,
  `pivot_val` varchar(255) NOT NULL,
  `risk_score` int DEFAULT NULL,
  `detected_dt` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`cluster_id`),
  KEY `idx_cluster_risk` (`risk_score`),
  CONSTRAINT `chk_risk` CHECK ((`risk_score` between 0 and 100)),
  CONSTRAINT `ncrp_pattern_cluster_chk_1` CHECK ((`risk_score` between 1 and 100))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ncrp_pattern_cluster`
--

LOCK TABLES `ncrp_pattern_cluster` WRITE;
/*!40000 ALTER TABLE `ncrp_pattern_cluster` DISABLE KEYS */;
INSERT INTO `ncrp_pattern_cluster` VALUES ('cl-001','SHARED_IP','103.21.44.9',70,'2026-10-08 18:30:44'),('cl-002','SHARED_BANK','HDFC0009876543',45,'2026-10-08 18:30:44'),('CLST-UUID-001','SHARED_BANK','98765432109876',85,'2026-09-10 17:06:33'),('CLST-UUID-002','RECURRING_IP','192.168.1.45',78,'2026-09-10 17:06:33'),('CLST-UUID-003','DOMAIN_PHISH','secure-bank-update-login.com',92,'2026-09-10 17:06:33'),('CLST-UUID-004','TELEGRAM_CHANNEL','t.me/CryptoHighReturns2026',88,'2026-09-10 17:06:33'),('CLST-UUID-005','PHONE_NUMBER','+919988776655',90,'2026-09-10 17:06:33'),('CLST-UUID-006','SHARED_BANK','11223344556677',81,'2026-09-10 17:06:33'),('CLST-UUID-007','RECURRING_IP','185.199.108.153',98,'2026-09-10 17:06:33'),('CLST-UUID-008','UPI_HANDLE','scamster@ybl',86,'2026-09-10 17:06:33'),('CLST-UUID-009','PHONE_NUMBER','+919633445566',75,'2026-09-10 17:06:33'),('CLST-UUID-010','DOMAIN_PHISH','instant-loan-approval-portal.in',80,'2026-09-10 17:06:33');
/*!40000 ALTER TABLE `ncrp_pattern_cluster` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ncrp_registrant_profile`
--

DROP TABLE IF EXISTS `ncrp_registrant_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncrp_registrant_profile` (
  `reg_id` varchar(36) NOT NULL,
  `full_name` varchar(120) NOT NULL,
  `email` varchar(150) NOT NULL,
  `phone` varchar(15) NOT NULL,
  `pass_hash` char(64) NOT NULL,
  `role_code` varchar(25) NOT NULL,
  `priv_lvl` smallint DEFAULT '1',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`reg_id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`),
  CONSTRAINT `chk_role` CHECK ((`role_code` in (_utf8mb4'ADMIN',_utf8mb4'INVESTIGATOR',_utf8mb4'VICTIM'))),
  CONSTRAINT `ncrp_registrant_profile_chk_1` CHECK ((`role_code` in (_utf8mb4'VICTIM',_utf8mb4'INVESTIGATOR',_utf8mb4'ADMIN')))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ncrp_registrant_profile`
--

LOCK TABLES `ncrp_registrant_profile` WRITE;
/*!40000 ALTER TABLE `ncrp_registrant_profile` DISABLE KEYS */;
INSERT INTO `ncrp_registrant_profile` VALUES ('reg-001','Admin User','admin@cciis.in','9000000001','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','ADMIN',5,'2026-10-08 18:30:44'),('reg-002','Insp. Ravi Kumar','ravi@cciis.in','9000000002','118b8d35a17bcf2c7d2d790509e12308dc6332c5d234f0098d2d6be6700bebb1','INVESTIGATOR',3,'2026-10-08 18:30:44'),('reg-003','Meena Iyer','meena@cciis.in','9000000003','20249749412d73a3f5799f6f1dcf910e7b4aa3ce4de133b1f8a63c044792a4e9','INVESTIGATOR',2,'2026-10-08 18:30:44'),('reg-004','Arjun Das','arjun@mail.com','9000000004','cacde1a09a72094c09893db6a8385767051f604025d042c983869f4fb30c66a7','VICTIM',1,'2026-10-08 18:30:44'),('reg-005','Priya Nair','priya@mail.com','9000000005','cacde1a09a72094c09893db6a8385767051f604025d042c983869f4fb30c66a7','VICTIM',1,'2026-10-08 18:30:44'),('USR-UUID-101','Aarav Sharma','aarav.sharma@example.com','+919876543210','ef92b778bafe771e89245b89ecbc08a44a4e166c0665911185cfd187678ac461','VICTIM',1,'2026-09-10 17:02:47'),('USR-UUID-102','Priya Verma','priya.verma@example.com','+919876543211','e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855','VICTIM',1,'2026-09-10 17:02:47'),('USR-UUID-103','Rohan Gupta','rohan.gupta@example.com','+919876543212','6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b','VICTIM',1,'2026-09-10 17:02:47'),('USR-UUID-104','Neha Iyer','neha.iyer@example.com','+919876543213','d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35','VICTIM',1,'2026-09-10 17:02:47'),('USR-UUID-105','Vikram Malhotra','vikram.malhotra@example.com','+919876543214','4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce','VICTIM',1,'2026-09-10 17:02:47'),('USR-UUID-106','Ananya Deshmukh','ananya.deshmukh@example.com','+919876543215','4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a','VICTIM',1,'2026-09-10 17:02:47'),('USR-UUID-107','Inspector Rajesh Kumar','rajesh.kumar@police.gov.in','+919123456780','ef92b778bafe771e89245b89ecbc08a44a4e166c0665911185cfd187678ac461','INVESTIGATOR',3,'2026-09-10 17:02:47'),('USR-UUID-108','Inspector Sunita Rao','sunita.rao@police.gov.in','+919123456782','e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855','INVESTIGATOR',3,'2026-09-10 17:02:47'),('USR-UUID-109','Inspector Manoj Tiwari','manoj.tiwari@police.gov.in','+919123456783','6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b','INVESTIGATOR',3,'2026-09-10 17:02:47'),('USR-UUID-110','Inspector Divya Nair','divya.nair@police.gov.in','+919123456784','d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35','INVESTIGATOR',3,'2026-09-10 17:02:47'),('USR-UUID-111','Superintendent Anil Mehta','anil.mehta@police.gov.in','+919123456781','4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce','ADMIN',5,'2026-09-10 17:02:47'),('USR-UUID-112','Commissioner K. S. Reddi','ks.reddi@police.gov.in','+919123456785','4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a','ADMIN',5,'2026-09-10 17:02:47');
/*!40000 ALTER TABLE `ncrp_registrant_profile` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ncrp_suspect_entity`
--

DROP TABLE IF EXISTS `ncrp_suspect_entity`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ncrp_suspect_entity` (
  `suspect_id` bigint NOT NULL AUTO_INCREMENT,
  `alias` varchar(100) DEFAULT 'UNKNOWN',
  `phone` varchar(15) DEFAULT NULL,
  `bank_acc` varchar(34) DEFAULT NULL,
  `ip_addr` varchar(45) DEFAULT NULL,
  `trace_notes` text,
  PRIMARY KEY (`suspect_id`),
  KEY `idx_suspect_phone` (`phone`),
  KEY `idx_suspect_ip` (`ip_addr`),
  KEY `idx_suspect_bank` (`bank_acc`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ncrp_suspect_entity`
--

LOCK TABLES `ncrp_suspect_entity` WRITE;
/*!40000 ALTER TABLE `ncrp_suspect_entity` DISABLE KEYS */;
INSERT INTO `ncrp_suspect_entity` VALUES (1,'CyberPhantom99','+919988776655','98765432109876','192.168.1.45','Linked with multiple fake billing portals.'),(2,'PhishMaster_X','+919811223344','11223344556677','10.0.0.12','Operates disposable domains for credential harvesting.'),(3,'CryptoKing_V','+919722334455','22334455667788','172.16.254.1','Core controller of fraudulent Telegram investment groups.'),(4,'LoanShark_Direct','+919633445566','33445566778899','192.168.0.102','Associated with predatory instant loan mobile apps.'),(5,'DarkWeb_Broker',NULL,'44556677889900','45.33.22.11','Sells verified KYC documents and compromised bank accounts.'),(6,'SimSwap_Gangs','+919544556677','55667788990011','10.10.20.30','Collaborates with inside telecom agents for port-outs.'),(7,'BotnetMaster',NULL,'66778899001122','185.199.108.153','Distributes ransomware payloads via phishing emails.'),(8,'SocialScammer_07','+919455667788','77889900112233','192.168.4.15','Hijacks social media handles for emergency fund scams.'),(9,'TaskScamOps','+919366778899','88990011223344','103.25.14.88','Runs part-time rating and review task scams.'),(10,'CardingKing','+919277889900','99001122334455','198.51.100.42','Executes unauthorized international e-commerce checkouts.'),(11,'FakeBank Caller','8111111111','SBIN0001234567','103.21.44.9','Vishing calls pretending to be bank'),(12,'Crypto Guru','8222222222','HDFC0009876543','45.77.12.200','Fake investment group'),(13,'OLX Buyer','8333333333',NULL,'103.21.44.9','QR code refund scam'),(14,'Unknown',NULL,'ICIC0004455667',NULL,'Mule account');
/*!40000 ALTER TABLE `ncrp_suspect_entity` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `vw_active_investigations`
--

DROP TABLE IF EXISTS `vw_active_investigations`;
/*!50001 DROP VIEW IF EXISTS `vw_active_investigations`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_active_investigations` AS SELECT 
 1 AS `doc_no`,
 1 AS `crime_type`,
 1 AS `stage_code`,
 1 AS `victim_name`,
 1 AS `investigator_name`,
 1 AS `filed_dt`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_officer_workload`
--

DROP TABLE IF EXISTS `vw_officer_workload`;
/*!50001 DROP VIEW IF EXISTS `vw_officer_workload`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_officer_workload` AS SELECT 
 1 AS `reg_id`,
 1 AS `full_name`,
 1 AS `total_cases`,
 1 AS `open_cases`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_pattern_summary`
--

DROP TABLE IF EXISTS `vw_pattern_summary`;
/*!50001 DROP VIEW IF EXISTS `vw_pattern_summary`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_pattern_summary` AS SELECT 
 1 AS `cluster_id`,
 1 AS `pattern_type`,
 1 AS `pivot_val`,
 1 AS `risk_score`,
 1 AS `linked_dockets`,
 1 AS `total_loss`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_suspect_case_history`
--

DROP TABLE IF EXISTS `vw_suspect_case_history`;
/*!50001 DROP VIEW IF EXISTS `vw_suspect_case_history`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_suspect_case_history` AS SELECT 
 1 AS `suspect_id`,
 1 AS `alias`,
 1 AS `phone`,
 1 AS `ip_addr`,
 1 AS `doc_no`,
 1 AS `crime_type`,
 1 AS `stage_code`,
 1 AS `loss_amt`,
 1 AS `conf_score`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_suspect_public`
--

DROP TABLE IF EXISTS `vw_suspect_public`;
/*!50001 DROP VIEW IF EXISTS `vw_suspect_public`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_suspect_public` AS SELECT 
 1 AS `suspect_id`,
 1 AS `alias`,
 1 AS `ip_addr`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping routines for database 'project_cciis'
--
/*!50003 DROP FUNCTION IF EXISTS `fn_case_age_days` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_case_age_days`(p_doc VARCHAR(30)) RETURNS int
    READS SQL DATA
    DETERMINISTIC
BEGIN
  DECLARE v_days INT;
  SELECT DATEDIFF(CURDATE(), DATE(filed_dt)) INTO v_days
  FROM ncrp_incident_docket WHERE doc_no = p_doc;
  RETURN v_days;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `fn_evidence_count` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_evidence_count`(p_doc VARCHAR(30)) RETURNS int
    READS SQL DATA
    DETERMINISTIC
BEGIN
  DECLARE v_cnt INT;
  SELECT COUNT(*) INTO v_cnt FROM ncrp_forensic_evidence WHERE doc_no = p_doc;
  RETURN v_cnt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `fn_get_suspect_count` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_get_suspect_count`(p_doc_no VARCHAR(30)) RETURNS int
    DETERMINISTIC
BEGIN
    DECLARE suspect_cnt INT;
    SELECT COUNT(*) INTO suspect_cnt 
    FROM NCRP_DOCKET_SUSPECT_LINK 
    WHERE doc_no = p_doc_no;
    RETURN suspect_cnt;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_assign_investigator` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_assign_investigator`(
    IN p_doc_no VARCHAR(30),
    IN p_officer_id VARCHAR(36)
)
BEGIN
    UPDATE NCRP_INCIDENT_DOCKET
    SET officer_id = p_officer_id, stage_code = 'TRIAGE'
    WHERE doc_no = p_doc_no;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_link_suspect` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_link_suspect`(
    IN p_doc VARCHAR(30), 
    IN p_suspect BIGINT, 
    IN p_conf DECIMAL(3,2)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    INSERT INTO ncrp_docket_suspect_link (doc_no, suspect_id, conf_score)
    VALUES (p_doc, p_suspect, p_conf)
    ON DUPLICATE KEY UPDATE conf_score = p_conf;

    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_process_high_risk_dockets` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_process_high_risk_dockets`()
BEGIN
    -- Correctly declare each local variable
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_doc VARCHAR(30);
    DECLARE v_loss NUMERIC(12,2);
    
    -- Declare cursor after variable declarations
    DECLARE cur_high_risk CURSOR FOR 
        SELECT doc_no, loss_amt FROM NCRP_INCIDENT_DOCKET WHERE loss_amt > 50000;
        
    -- Declare handlers last
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur_high_risk;
    read_loop: LOOP
        FETCH cur_high_risk INTO v_doc, v_loss;
        IF done THEN
            LEAVE read_loop;
        END IF;
        -- Processing logic placeholder (e.g., flagging for priority audit)
    END LOOP;
    CLOSE cur_high_risk;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_register_docket` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_register_docket`(
    IN p_doc VARCHAR(30), 
    IN p_victim VARCHAR(36), 
    IN p_officer VARCHAR(36),
    IN p_event TIMESTAMP, 
    IN p_crime VARCHAR(50), 
    IN p_details TEXT, 
    IN p_loss DECIMAL(12,2)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        -- Re-signal the error to the calling application if needed
        RESIGNAL;
    END;

    START TRANSACTION;

    INSERT INTO ncrp_incident_docket (doc_no, victim_id, officer_id, event_dt, crime_type, details, loss_amt)
    VALUES (p_doc, p_victim, p_officer, p_event, p_crime, p_details, p_loss);

    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_suspect_cases` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_suspect_cases`(
    IN p_suspect BIGINT
)
BEGIN
    SELECT d.doc_no, d.crime_type, d.stage_code, d.loss_amt, l.conf_score
    FROM ncrp_docket_suspect_link l
    JOIN ncrp_incident_docket d ON d.doc_no = l.doc_no
    WHERE l.suspect_id = p_suspect
    ORDER BY d.filed_dt DESC;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_update_stage` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_update_stage`(
    IN p_doc VARCHAR(30), 
    IN p_stage VARCHAR(30)
)
BEGIN
    UPDATE ncrp_incident_docket 
    SET stage_code = p_stage 
    WHERE doc_no = p_doc;

    IF ROW_COUNT() = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Docket not found or stage unchanged';
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Final view structure for view `vw_active_investigations`
--

/*!50001 DROP VIEW IF EXISTS `vw_active_investigations`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_active_investigations` AS select `d`.`doc_no` AS `doc_no`,`d`.`crime_type` AS `crime_type`,`d`.`stage_code` AS `stage_code`,`v`.`full_name` AS `victim_name`,`p`.`full_name` AS `investigator_name`,`d`.`filed_dt` AS `filed_dt` from ((`ncrp_incident_docket` `d` join `ncrp_registrant_profile` `v` on((`d`.`victim_id` = `v`.`reg_id`))) left join `ncrp_registrant_profile` `p` on((`d`.`officer_id` = `p`.`reg_id`))) where (`d`.`stage_code` <> 'CLOSED') */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_officer_workload`
--

/*!50001 DROP VIEW IF EXISTS `vw_officer_workload`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_officer_workload` AS select `r`.`reg_id` AS `reg_id`,`r`.`full_name` AS `full_name`,count(`d`.`doc_no`) AS `total_cases`,sum((`d`.`stage_code` <> 'CLOSED')) AS `open_cases` from (`ncrp_registrant_profile` `r` join `ncrp_incident_docket` `d` on((`d`.`officer_id` = `r`.`reg_id`))) group by `r`.`reg_id`,`r`.`full_name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_pattern_summary`
--

/*!50001 DROP VIEW IF EXISTS `vw_pattern_summary`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_pattern_summary` AS select `c`.`cluster_id` AS `cluster_id`,`c`.`pattern_type` AS `pattern_type`,`c`.`pivot_val` AS `pivot_val`,`c`.`risk_score` AS `risk_score`,count(`p`.`doc_no`) AS `linked_dockets`,ifnull(sum(`d`.`loss_amt`),0) AS `total_loss` from ((`ncrp_pattern_cluster` `c` left join `ncrp_docket_pattern_link` `p` on((`p`.`cluster_id` = `c`.`cluster_id`))) left join `ncrp_incident_docket` `d` on((`d`.`doc_no` = `p`.`doc_no`))) group by `c`.`cluster_id`,`c`.`pattern_type`,`c`.`pivot_val`,`c`.`risk_score` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_suspect_case_history`
--

/*!50001 DROP VIEW IF EXISTS `vw_suspect_case_history`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_suspect_case_history` AS select `s`.`suspect_id` AS `suspect_id`,`s`.`alias` AS `alias`,`s`.`phone` AS `phone`,`s`.`ip_addr` AS `ip_addr`,`d`.`doc_no` AS `doc_no`,`d`.`crime_type` AS `crime_type`,`d`.`stage_code` AS `stage_code`,`d`.`loss_amt` AS `loss_amt`,`l`.`conf_score` AS `conf_score` from ((`ncrp_suspect_entity` `s` join `ncrp_docket_suspect_link` `l` on((`l`.`suspect_id` = `s`.`suspect_id`))) join `ncrp_incident_docket` `d` on((`d`.`doc_no` = `l`.`doc_no`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_suspect_public`
--

/*!50001 DROP VIEW IF EXISTS `vw_suspect_public`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `vw_suspect_public` AS select `ncrp_suspect_entity`.`suspect_id` AS `suspect_id`,`ncrp_suspect_entity`.`alias` AS `alias`,`ncrp_suspect_entity`.`ip_addr` AS `ip_addr` from `ncrp_suspect_entity` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-09  0:24:44
