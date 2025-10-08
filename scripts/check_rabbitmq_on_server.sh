#!/bin/bash
# Check RabbitMQ on remote server
# Usage: ./scripts/check_rabbitmq_on_server.sh

echo "==================================================================="
echo "Checking RabbitMQ on 10.10.10.150..."
echo "==================================================================="

# Check if RabbitMQ is listening on port 5672
echo ""
echo "[1] Checking if port 5672 is open..."
ssh prisma@10.10.10.150 "sudo netstat -tlnp | grep 5672 || echo 'Port 5672 not listening'"

echo ""
echo "[2] Checking RabbitMQ service status..."
ssh prisma@10.10.10.150 "sudo systemctl status rabbitmq-server || echo 'RabbitMQ systemd service not found'"

echo ""
echo "[3] Checking RabbitMQ via rabbitmqctl..."
ssh prisma@10.10.10.150 "sudo rabbitmqctl status || echo 'rabbitmqctl not available'"

echo ""
echo "[4] Checking for RabbitMQ in Docker/K8s..."
ssh prisma@10.10.10.150 "docker ps | grep rabbit || echo 'No RabbitMQ in Docker'"
ssh prisma@10.10.10.150 "sudo crictl ps | grep rabbit || echo 'No RabbitMQ in containerd'"

echo ""
echo "==================================================================="
echo "DONE"
echo "==================================================================="

