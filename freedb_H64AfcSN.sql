-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: sql.freedb.tech:3306
-- Generation Time: Nov 12, 2026 at 10:55 PM
-- Server version: 8.0.46-0ubuntu0.22.04.5
-- PHP Version: 8.4.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `freedb_H64AfcSN`
--

-- --------------------------------------------------------

--
-- Table structure for table `APPROVISIONNEMENT`
--

CREATE TABLE `APPROVISIONNEMENT` (
  `id_appro` int NOT NULL,
  `date_appro` date NOT NULL,
  `id_produit` int NOT NULL,
  `quantite` int NOT NULL,
  `prix_achat` decimal(12,2) NOT NULL
) ;

--
-- Dumping data for table `APPROVISIONNEMENT`
--

INSERT INTO `APPROVISIONNEMENT` (`id_appro`, `date_appro`, `id_produit`, `quantite`, `prix_achat`) VALUES
(1, '2026-11-01', 1, 10, 280000.00),
(2, '2026-11-02', 2, 30, 10000.00),
(3, '2026-11-03', 3, 50, 4500.00),
(4, '2026-11-04', 4, 5, 95000.00);

-- --------------------------------------------------------

--
-- Table structure for table `categorie_produit`
--

CREATE TABLE `categorie_produit` (
  `id_categorie` int NOT NULL,
  `libelle` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `categorie_produit`
--

INSERT INTO `categorie_produit` (`id_categorie`, `libelle`) VALUES
(2, 'Accessoires'),
(1, 'Informatique'),
(3, 'Mobilier');

-- --------------------------------------------------------

--
-- Table structure for table `DEPENSE`
--

CREATE TABLE `DEPENSE` (
  `id_depense` int NOT NULL,
  `date_depense` date NOT NULL,
  `libelle` varchar(200) NOT NULL,
  `montant` decimal(12,2) NOT NULL
) ;

--
-- Dumping data for table `DEPENSE`
--

INSERT INTO `DEPENSE` (`id_depense`, `date_depense`, `libelle`, `montant`) VALUES
(1, '2026-11-05', 'Facture electricite', 25000.00),
(2, '2026-11-06', 'Transport marchandises', 15000.00),
(3, '2026-11-07', 'Entretien boutique', 10000.00);

-- --------------------------------------------------------

--
-- Table structure for table `produit`
--

CREATE TABLE `produit` (
  `id_produit` int NOT NULL,
  `designation` varchar(150) NOT NULL,
  `prix_vente` decimal(12,2) NOT NULL,
  `id_categorie` int NOT NULL
) ;

--
-- Dumping data for table `produit`
--

INSERT INTO `produit` (`id_produit`, `designation`, `prix_vente`, `id_categorie`) VALUES
(1, 'Ordinateur portable', 350000.00, 1),
(2, 'Clavier sans fil', 15000.00, 2),
(3, 'Souris optique', 7500.00, 2),
(4, 'Bureau professionnel', 125000.00, 3),
(5, 'FORMATION CHATBOT', 120000.00, 1);

-- --------------------------------------------------------

--
-- Table structure for table `users_accounts`
--

CREATE TABLE `users_accounts` (
  `id` int NOT NULL,
  `login` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `state_account` tinyint(1) NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `users_accounts`
--

INSERT INTO `users_accounts` (`id`, `login`, `password`, `state_account`) VALUES
(1, 'admin', 'scrypt:32768:8:1$4zCefebdio6zM6e1$a1079f883c7ccfd5191296d4b06399cad2a35b0c6bb0c7959e3651216c4906dcf5c82e1e36f59bdf4ade45f9d48d344b58178428e890e00008138b5db0a2aa6c', 1),
(2, 'gestionnaire', 'HASH_GESTIONNAIRE', 1),
(3, 'utilisateur', 'HASH_UTILISATEUR', 1);

-- --------------------------------------------------------

--
-- Table structure for table `vente`
--

CREATE TABLE `vente` (
  `id_vente` int NOT NULL,
  `date_vente` date NOT NULL,
  `id_produit` int NOT NULL,
  `quantite` int NOT NULL,
  `prix_unitaire` decimal(12,2) NOT NULL
) ;

--
-- Dumping data for table `vente`
--

INSERT INTO `vente` (`id_vente`, `date_vente`, `id_produit`, `quantite`, `prix_unitaire`) VALUES
(1, '2026-11-05', 1, 2, 350000.00),
(2, '2026-11-06', 2, 5, 15000.00),
(4, '2026-11-01', 2, 123, 12345.00);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `APPROVISIONNEMENT`
--
ALTER TABLE `APPROVISIONNEMENT`
  ADD PRIMARY KEY (`id_appro`),
  ADD KEY `fk_appro_produit` (`id_produit`);

--
-- Indexes for table `categorie_produit`
--
ALTER TABLE `categorie_produit`
  ADD PRIMARY KEY (`id_categorie`),
  ADD UNIQUE KEY `libelle` (`libelle`);

--
-- Indexes for table `DEPENSE`
--
ALTER TABLE `DEPENSE`
  ADD PRIMARY KEY (`id_depense`);

--
-- Indexes for table `produit`
--
ALTER TABLE `produit`
  ADD PRIMARY KEY (`id_produit`),
  ADD KEY `fk_produit_categorie` (`id_categorie`);

--
-- Indexes for table `users_accounts`
--
ALTER TABLE `users_accounts`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `login` (`login`);

--
-- Indexes for table `vente`
--
ALTER TABLE `vente`
  ADD PRIMARY KEY (`id_vente`),
  ADD KEY `fk_vente_produit` (`id_produit`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `APPROVISIONNEMENT`
--
ALTER TABLE `APPROVISIONNEMENT`
  MODIFY `id_appro` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `categorie_produit`
--
ALTER TABLE `categorie_produit`
  MODIFY `id_categorie` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `DEPENSE`
--
ALTER TABLE `DEPENSE`
  MODIFY `id_depense` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `produit`
--
ALTER TABLE `produit`
  MODIFY `id_produit` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `users_accounts`
--
ALTER TABLE `users_accounts`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `vente`
--
ALTER TABLE `vente`
  MODIFY `id_vente` int NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `APPROVISIONNEMENT`
--
ALTER TABLE `APPROVISIONNEMENT`
  ADD CONSTRAINT `fk_appro_produit` FOREIGN KEY (`id_produit`) REFERENCES `produit` (`id_produit`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `produit`
--
ALTER TABLE `produit`
  ADD CONSTRAINT `fk_produit_categorie` FOREIGN KEY (`id_categorie`) REFERENCES `categorie_produit` (`id_categorie`) ON DELETE RESTRICT ON UPDATE CASCADE;

--
-- Constraints for table `vente`
--
ALTER TABLE `vente`
  ADD CONSTRAINT `fk_vente_produit` FOREIGN KEY (`id_produit`) REFERENCES `produit` (`id_produit`) ON DELETE RESTRICT ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
