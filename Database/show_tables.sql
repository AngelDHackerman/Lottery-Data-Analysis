show TABLES;

SELECT * FROM Premios;

SELECT * FROM Sorteos;

SELECT * FROM calendar_sorteos;

SHOW CREATE TABLE Premios;

-- See details for Premios
DESCRIBE Premios;

-- See details for Sorteos
DESCRIBE Sorteos;

DESCRIBE calendar_sorteos;

DESCRIBE letter_combinations;

-- check there is not text values in monto
SELECT monto FROM Premios WHERE monto NOT REGEXP '^[0-9]+(\.[0-9]{1,2})?$';

SELECT * FROM Premios ORDER BY monto;

SELECT * FROM Premios 
WHERE vendedor = "NO VENDIDO"
ORDER BY monto;

SELECT * FROM calendar_sorteos
ORDER BY sorteo_fecha ASC;

SELECT * FROM letter_combinations;

SELECT * FROM Sorteos
ORDER BY fecha_sorteo;

SELECT * FROM Premios
ORDER BY numero_sorteo;

-- count total rows
SELECT COUNT(*) AS total_rows
FROM Premios;