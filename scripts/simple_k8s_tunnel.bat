@echo off
echo ================================================================================
echo Starting Simple Kubernetes SSH Tunnel
echo ================================================================================
echo.
echo This will create a tunnel from localhost:6443 to 10.10.100.102:6443
echo via bastion host 10.10.100.3
echo.
echo When prompted, enter password: PASSW0RD
echo.
echo Keep this window open while using kubectl!
echo ================================================================================
echo.

ssh -N -L 6443:10.10.100.102:6443 root@10.10.100.3
