@echo off
echo ================================================================================
echo Direct SSH Connection to Kubernetes Cluster
echo ================================================================================
echo.
echo This will connect you directly to the bastion host
echo From there you can access k9s
echo.
echo Password: PASSW0RD
echo.
echo Once connected:
echo 1. Type: ssh prisma@10.10.100.113 (needs SSH key)
echo    OR
echo 2. Type: kubectl get pods -n panda (if kubectl is on bastion)
echo ================================================================================
echo.

ssh root@10.10.100.3
