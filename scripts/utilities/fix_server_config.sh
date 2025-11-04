#!/bin/bash
# ============================================================================
# Fix Focus Server Configuration for New Environment
# ============================================================================

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   Fixing Focus Server Configuration                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"

# Get Focus Server pod name
POD_NAME=$(kubectl get pods -n panda | grep focus-server | awk '{print $1}')
echo "Found Focus Server pod: $POD_NAME"

# Backup original config
echo "Creating backup..."
kubectl exec -n panda $POD_NAME -- cp /home/prisma/pz/config/py/default_config.py /home/prisma/pz/config/py/default_config.py.backup.$(date +%Y%m%d_%H%M%S)

# Fix RabbitMQ configuration
echo "Fixing RabbitMQ configuration..."
kubectl exec -n panda $POD_NAME -- sed -i "s/broker_server = 'data-rabbitmq.prismaphotonics.net'/broker_server = 'rabbitmq-panda.panda'/g" /home/prisma/pz/config/py/default_config.py
kubectl exec -n panda $POD_NAME -- sed -i "s/broker_port = 5671/broker_port = 5672/g" /home/prisma/pz/config/py/default_config.py
kubectl exec -n panda $POD_NAME -- sed -i "s/broker_protocol = 'amqps'/broker_protocol = 'amqp'/g" /home/prisma/pz/config/py/default_config.py

# Fix Focus View URL
echo "Fixing Focus View URL..."
kubectl exec -n panda $POD_NAME -- sed -i "s|focus_view_url = 'http://10.10.100.113'|focus_view_url = 'http://10.10.10.100'|g" /home/prisma/pz/config/py/default_config.py

# Verify changes
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Verifying changes:"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "RabbitMQ Configuration:"
kubectl exec -n panda $POD_NAME -- grep -A 5 "class Broker:" /home/prisma/pz/config/py/default_config.py | grep -E "broker_server|broker_port|broker_protocol"
echo ""
echo "Focus View URL:"
kubectl exec -n panda $POD_NAME -- grep focus_view_url /home/prisma/pz/config/py/default_config.py
echo ""

# Restart pod
echo "═══════════════════════════════════════════════════════════"
echo "Restarting Focus Server pod..."
echo "═══════════════════════════════════════════════════════════"
kubectl delete pod $POD_NAME -n panda

echo "Waiting for pod to restart..."
sleep 5
kubectl wait --for=condition=ready pod -l app=panda-panda-focus-server -n panda --timeout=120s

NEW_POD=$(kubectl get pods -n panda | grep focus-server | awk '{print $1}')
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                   SUCCESS!                                 ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Configuration updated"
echo "✅ Focus Server restarted"
echo "✅ New pod: $NEW_POD"
echo ""
echo "Changes made:"
echo "  • RabbitMQ: rabbitmq-panda.panda:5672 (amqp)"
echo "  • Focus View: http://10.10.10.100"
echo ""

