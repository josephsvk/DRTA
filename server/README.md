### Comont prompt
**Buid container**  
sudo docker compose build
sudo docker compose up --build

**Run comtainer**   
sudo docker compose up

### Local Run
**Vygenerujte certifikát s vlastným podpisom**
```console
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```
### Run interactive container 
```console
docker compose exec -it totop-server bash
```