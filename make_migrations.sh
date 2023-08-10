#!/bin/bash
sudo docker exec notifications_sprint_2-web-1 alembic revision --autogenerate -m "init"
sudo docker exec notifications_sprint_2-web-1 alembic upgrade head
