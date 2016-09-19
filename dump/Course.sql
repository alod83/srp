-- phpMyAdmin SQL Dump
-- version 4.5.2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Creato il: Lug 15, 2016 alle 00:03
-- Versione del server: 10.1.13-MariaDB
-- Versione PHP: 5.5.35

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `OSIRIS`
--

-- --------------------------------------------------------

--
-- Struttura della tabella `Course`
--

CREATE TABLE `Course` (
  `id` int(11) NOT NULL,
  `value` varchar(10) NOT NULL,
  `min` decimal(10,2) NOT NULL,
  `max` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dump dei dati per la tabella `Course`
--

INSERT INTO `Course` (`id`, `value`, `min`, `max`) VALUES
(1, 'N', '0.00', '22.50'),
(2, 'N', '337.50', '360.00'),
(3, 'NE', '22.50', '67.50'),
(4, 'E', '67.50', '112.50'),
(5, 'SE', '112.50', '157.50'),
(6, 'S', '157.50', '202.50'),
(7, 'SW', '202.50', '247.50'),
(8, 'W', '247.50', '292.50'),
(9, 'NW', '292.50', '337.50');

--
-- Indici per le tabelle scaricate
--

--
-- Indici per le tabelle `Course`
--
ALTER TABLE `Course`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT per le tabelle scaricate
--

--
-- AUTO_INCREMENT per la tabella `Course`
--
ALTER TABLE `Course`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
