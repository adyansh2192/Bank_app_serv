# TrustBank microservices demo

A training/demo bank application with a static HTML/CSS/JavaScript frontend served by NGINX, two Flask microservices, and MySQL. It includes Home, Registration, Sign in, Savings, and Personal account screens.

> Demo only. It is not production banking software. Do not enter real financial information.

## Architecture

Browser -> NGINX (frontend + reverse proxy) -> auth-service / account-service -> MySQL

## Run in VS Code

1. Install Git, Docker Desktop, the Docker Compose plugin, and VS Code.
2. Extract/open this folder in VS Code.
3. In the VS Code terminal:

```bash
cp .env.example .env
```

4. Replace every value in `.env`. Generate a JWT secret with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

5. Start the complete application:

```bash
docker compose up -d --build
docker compose ps
docker compose logs -f
```

6. Browse to `http://localhost`. Register and sign in.
7. Stop with `docker compose down`. To delete the database volume too, use `docker compose down -v`.

## Verify the API and database

```bash
curl http://localhost/api/auth/health
curl http://localhost/api/accounts/health
docker exec -it bank-mysql mysql -ubankuser -p bankdb
docker compose ps
docker compose logs --tail=100 auth-service account-service nginx mysql
```

Inside MySQL:

```sql
SHOW TABLES;
SELECT id, full_name, email, created_at FROM users;
SELECT id, user_id, account_number, account_type, balance FROM accounts;
EXIT;
```

## Push to GitHub

Create an empty GitHub repository first, without initializing it with a README. Then run:

```bash
git init
git add .
git commit -m "Build TrustBank microservices application"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

Never commit `.env`.

## Clone and deploy on an Ubuntu EC2 server

Open inbound TCP 22 from your IP and TCP 80 from the required audience. Connect through SSH, then:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl git
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
cd YOUR_REPOSITORY
cp .env.example .env
nano .env
docker compose up -d --build
docker compose ps
curl http://localhost/api/auth/health
```

Open `http://YOUR_EC2_PUBLIC_IP` in a browser. If port 80 is already occupied by host NGINX, either stop it with `sudo systemctl stop nginx`, or change the compose mapping to `8080:80` and proxy the host NGINX to port 8080.

## Production hardening backlog

Use HTTPS, a secrets manager, a managed database/private subnet, request validation, rate limiting, CSRF strategy, refresh-token rotation, audit logging, monitoring, backups, database migrations, automated tests, vulnerability scanning, and least-privilege network rules before considering a real deployment.
