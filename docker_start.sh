docker stop Reviews
docker rm -v Reviews

docker run --name="Reviews" \
	   -v /root/reviews:/app \
	   --restart=always \
           -it -d luomoxingkong/scarpy_remote_cn_ubuntu1604 \
           bash 
docker exec -it Reviews pip3 install -r /app/requirements.txt

