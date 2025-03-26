@echo off
echo === Stopping all running Docker containers ===
docker stop $(docker ps -aq) 2>nul || echo No containers to stop

echo === Removing all unused containers, networks, images, and volumes ===
docker system prune -a --volumes -f

echo === Building Docker image ===
docker build -t policy_django .

echo === Running container ===
docker run -d -p 8000:8000 --name policy_django_container policy_django

echo === Waiting for container to start... ===
timeout /t 5 /nobreak >nul

echo === Running migrations ===
docker exec policy_django_container python manage.py migrate

echo === Setup complete ===
echo Access the application at http://localhost:8000
pause