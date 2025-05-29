CREATE DATABASE IF NOT EXISTS tvm;

USE tvm;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS sub_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS advisory_texts (
    category INT NOT NULL,
    sub_category INT NOT NULL,
    text TEXT NOT NULL,
    PRIMARY KEY (category, sub_category),
    FOREIGN KEY (category) REFERENCES categories(id),
    FOREIGN KEY (sub_category) REFERENCES sub_categories(id)
);