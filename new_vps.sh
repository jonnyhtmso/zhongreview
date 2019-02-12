yum install -y git
yum install -y docker || systemctl daemon-reload || service docker restart
bash docker_start.sh 
cp -rnf .ssh ~/ 

