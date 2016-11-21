-- phpMyAdmin SQL Dump
-- version 4.5.2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Creato il: Nov 21, 2016 alle 15:30
-- Versione del server: 10.1.13-MariaDB
-- Versione PHP: 5.5.35

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `DATI_AIS`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `Malta`
--

CREATE TABLE `Malta` (
  `vessel_id` int(11) NOT NULL,
  `MMSI` int(11) NOT NULL,
  `TIME` varchar(30) NOT NULL,
  `TIMESTAMP` datetime DEFAULT NULL,
  `LAT` varchar(30) NOT NULL,
  `LON` varchar(30) NOT NULL,
  `LATITUDE` decimal(18,15) NOT NULL,
  `LONGITUDE` decimal(18,15) NOT NULL,
  `NAME` varchar(50) NOT NULL,
  `SPEED` decimal(10,2) NOT NULL,
  `COURSE` decimal(10,2) NOT NULL,
  `DATASET` enum('TRAINING','TEST','','') NOT NULL DEFAULT 'TRAINING',
  `NEXT_STATUS` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `Malta`
--
ALTER TABLE `Malta`
  ADD PRIMARY KEY (`vessel_id`),
  ADD UNIQUE KEY `MMSI` (`MMSI`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `Malta`
--
ALTER TABLE `Malta`
  MODIFY `vessel_id` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
