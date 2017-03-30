!#/bin/bash

mkfifo udptunnel
nc -l -u -p 14550 < udptunnel | nc localhost 2222 > udptunnel
