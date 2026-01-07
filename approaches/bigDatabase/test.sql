-- Create Database
CREATE DATABASE UN_Country_DB;
USE UN_Country_DB;

-- Table: Country
CREATE TABLE Country (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    iso_alpha_2 CHAR(2) NOT NULL,
    iso_alpha_3 CHAR(3) NOT NULL,
    un_code INT NOT NULL UNIQUE,
    region VARCHAR(50),
    subregion VARCHAR(50),
    population BIGINT,
    gdp DECIMAL(15, 2),
    currency VARCHAR(10),
    official_language VARCHAR(50)
);

-- Table: Economic Indicators
CREATE TABLE EconomicIndicators (
    indicator_id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT NOT NULL,
    indicator_name VARCHAR(100) NOT NULL,
    value DECIMAL(15, 2),
    year INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);

-- Table: Trade Partners
CREATE TABLE TradePartners (
    trade_id INT AUTO_INCREMENT PRIMARY KEY,
    exporting_country_id INT NOT NULL,
    importing_country_id INT NOT NULL,
    trade_value DECIMAL(15, 2) NOT NULL,
    year INT NOT NULL,
    FOREIGN KEY (exporting_country_id) REFERENCES Country(country_id),
    FOREIGN KEY (importing_country_id) REFERENCES Country(country_id)
);

-- Table: Agreements
CREATE TABLE Agreements (
    agreement_id INT AUTO_INCREMENT PRIMARY KEY,
    country_id INT NOT NULL,
    agreement_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    FOREIGN KEY (country_id) REFERENCES Country(country_id)
);