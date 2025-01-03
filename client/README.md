

###Príkaz docker compose runumožňuje interaktívny prístup ku kontajneru. Spustite kontajner nasledovne:
sudo docker compose run drta-client


###Ak je kontajner spustený, môžete sa pripojiť k bežiacemu kontajneru pomocou:
sudo docker compose up
sudo docker compose up --build                    
sudo docker exec -it DRTA-Client bash
python form.py

###Manuálne testovanie: 
Ak potrebujete debugovať, spustite kontajner s príkazom:
sudo docker run -it --rm --name test-drta-client client-drta-client bash

###logs : 
docker logs DRTA-Client
docker info

###Dôležité:
Ak chcete, aby formulár bežal na vašu konzolu, zadajte príkaz runnamiesto up.
Ak chcete spustiť formulár automaticky pri každom štarte kontajnera, skontrolujte, či je správne nakonfigurovaný príkaz v docker-compose.yml.
