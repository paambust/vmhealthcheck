#!/bin/bash

HOSTNAME=$(hostname)
DATE=$(date '+%Y-%m-%d %H:%M:%S')

CPU_THRESHOLD=80
MEM_THRESHOLD=80
DISK_THRESHOLD=80
PING_TARGET="8.8.8.8"

echo "====================================="
echo " VM HEALTH CHECK REPORT"
echo " Host: $HOSTNAME"
echo " Date: $DATE"
echo "====================================="

### CPU USAGE ###
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8}')
CPU_USAGE=${CPU_USAGE%.*}

echo "CPU Usage: $CPU_USAGE%"
if [ "$CPU_USAGE" -ge "$CPU_THRESHOLD" ]; then
  echo "⚠️  CPU usage is HIGH"
else
  echo "✅ CPU usage is OK"
fi

echo "-------------------------------------"

### MEMORY USAGE ###
MEM_TOTAL=$(free -m | awk '/Mem:/ {print $2}')
MEM_USED=$(free -m | awk '/Mem:/ {print $3}')
MEM_USAGE=$((MEM_USED * 100 / MEM_TOTAL))

echo "Memory Usage: $MEM_USAGE%"
if [ "$MEM_USAGE" -ge "$MEM_THRESHOLD" ]; then
  echo "⚠️  Memory usage is HIGH"
else
  echo "✅ Memory usage is OK"
fi

echo "-------------------------------------"

### DISK USAGE ###
echo "Disk Usage:"
df -h | awk 'NR==1 || $5+0 >= '"$DISK_THRESHOLD"' {print $0}'

DISK_ALERT=$(df -h | awk '$5+0 >= '"$DISK_THRESHOLD"' {print $5}' | wc -l)
if [ "$DISK_ALERT" -gt 0 ]; then
  echo "⚠️  Disk usage is HIGH"
else
  echo "✅ Disk usage is OK"
fi

echo "-------------------------------------"

### NETWORK CHECK ###
ping -c 2 $PING_TARGET > /dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "✅ Network connectivity OK (Ping $PING_TARGET)"
else
  echo "❌ Network issue detected"
fi

echo "-------------------------------------"

### SYSTEM LOAD ###
LOAD_AVG=$(uptime | awk -F'load average:' '{ print $2 }')
echo "Load Average:$LOAD_AVG"

echo "-------------------------------------"

### UPTIME ###
echo "Uptime:"
uptime -p

echo "-------------------------------------"

### OPTIONAL: SERVICE CHECK ###
SERVICES=("sshd" "cron")

for service in "${SERVICES[@]}"; do
  systemctl is-active --quiet $service
  if [ $? -eq 0 ]; then
    echo "✅ Service $service is running"
  else
    echo "❌ Service $service is NOT running"
  fi
done

echo "====================================="
echo " Health check completed"
echo "====================================="
