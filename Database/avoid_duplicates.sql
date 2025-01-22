
-- Adding numero_sorteo as unique key value in Sorteos table
ALTER TABLE Sorteos
ADD UNIQUE (numero_sorteo);

-- Making sure values numero_sorteo, numero_premiado, letras 
-- as unique values in Premios table for avoid duplicates
ALTER TABLE Premios
ADD UNIQUE key unique_premios (numero_sorteo, numero_premiado, letras);