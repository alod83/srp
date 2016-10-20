-- phpMyAdmin SQL Dump
-- version 4.5.2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Creato il: Ott 20, 2016 alle 15:16
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
-- Struttura della tabella `Malta_Pattern`
--

CREATE TABLE `Malta_Pattern` (
  `pattern_id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `pattern` varchar(100) NOT NULL,
  `course_id` varchar(10) NOT NULL,
  `speed_id` varchar(10) NOT NULL,
  `vessel_id` int(11) NOT NULL,
  `year` int(11) NOT NULL,
  `month` int(11) NOT NULL,
  `day` int(11) NOT NULL,
  `sh` int(11) NOT NULL,
  `eh` int(11) NOT NULL,
  `row` int(11) NOT NULL,
  `col` int(11) NOT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

