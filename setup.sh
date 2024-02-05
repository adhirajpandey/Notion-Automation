docker compose up > /dev/null
docker build -t notion_auto .
docker run -d --network=host --restart unless-stopped notion_auto
