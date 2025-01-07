### Common prompt 

**Run the setup form:**     
```**bash**
sudo docker compose run drta-client --setup
```
**Run the agent:**  
```markdown
sudo docker compose run drta-client --run
```
**Run the registration script:**    
```console
sudo docker compose run drta-client --register
```
### Príkaz docker compose run umožňuje interaktívny prístup ku kontajneru. Spustite kontajner nasledovne:
```console
sudo docker compose run drta-client
```

### Ak je kontajner spustený, môžete sa pripojiť k bežiacemu kontajneru pomocou:
sudo docker compose up
sudo docker compose up --build                    
sudo docker exec -it DRTA-Client bash
python form.py

### Manuálne testovanie: 
Ak potrebujete debugovať, spustite kontajner s príkazom:
sudo docker run -it --rm --name test-drta-client client-drta-client bash
docker exec -it DRTA-Client sh

### logs : 
docker logs DRTA-Client
docker info
docker-compose config

### Dôležité:
Ak chcete, aby formulár bežal na vašu konzolu, zadajte príkaz runnamiesto up.
Ak chcete spustiť formulár automaticky pri každom štarte kontajnera, skontrolujte, či je správne nakonfigurovaný príkaz v docker-compose.yml.

### Build container 
sudo docker compose build

### Cleaning
sudo docker 