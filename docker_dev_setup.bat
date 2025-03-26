@echo off
echo === Stopping existing development container ===
docker stop policy_django_dev 2>nul || echo No development container to stop

echo === Removing existing development container ===
docker rm policy_django_dev 2>nul || echo No development container to remove

echo === Building Docker image (if needed) ===
docker build -t policy_django .

echo === Running development container ===
docker run -it --rm ^
    -p 8001:8000 ^
    -v "%cd%:/app" ^
    --name policy_django_dev ^
    policy_django ^
    sh -c "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"

echo === Development container running ===
echo Access the application at http://localhost:8001
echo Press Ctrl+C to stop the container