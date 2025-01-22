-- Create table for calendar sorteos
CREATE TABLE IF NOT EXISTS calendar_sorteos(
    id INT AUTO_INCREMENT PRIMARY KEY,
    sorteo_fecha DATE NOT NULL,
    sorteo_tipo VARCHAR(255) NOT NULL,
    numero_sorteo INT NOT NULL,
    premio_mayor INT NOT NULL
);

-- Create table for letter combinations
CREATE TABLE IF NOT EXISTS letter_combinations(
    id INT AUTO_INCREMENT PRIMARY KEY,
    combinations VARCHAR(10) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NOT NULL
);


