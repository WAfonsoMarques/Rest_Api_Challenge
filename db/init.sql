DROP DATABASE IF EXISTS `challengedb`;
CREATE DATABASE `challengedb`;

CREATE USER IF NOT EXISTS 'challenge'@'%' IDENTIFIED BY 'challengepass';
GRANT all privileges ON challengedb.* TO 'challenge'@'%';
FLUSH PRIVILEGES
