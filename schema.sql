CREATE TABLE IF NOT EXISTS categorie_produit (
  id_categorie INT AUTO_INCREMENT PRIMARY KEY,
  libelle VARCHAR(120) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS produit (
  id_produit INT AUTO_INCREMENT PRIMARY KEY,
  designation VARCHAR(180) NOT NULL,
  prix_vente DECIMAL(12,2) NOT NULL DEFAULT 0,
  id_categorie INT NOT NULL,
  CONSTRAINT fk_produit_categorie FOREIGN KEY (id_categorie)
    REFERENCES categorie_produit(id_categorie)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS vente (
  id_vente INT AUTO_INCREMENT PRIMARY KEY,
  date_vente DATE NOT NULL,
  id_produit INT NOT NULL,
  quantite INT NOT NULL,
  prix_unitaire DECIMAL(12,2) NOT NULL,
  CONSTRAINT fk_vente_produit FOREIGN KEY (id_produit)
    REFERENCES produit(id_produit)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
