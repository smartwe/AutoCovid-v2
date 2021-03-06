import os

#로컬환경
mongo_host = "localhost"
mongo_port = 27017
authcode = "authcode"
logconfig = "logging_local.json"
adsense_client = "ca-pub-1463419267666050"
#도커환경
if os.environ.get('DOCKER-MONGO-HOST'):
    mongo_host = str(os.environ.get('DOCKER-MONGO-HOST'))
    mongo_port = int(os.environ.get('DOCKER-MONGO-PORT'))
    authcode = str(os.environ.get('DOCKER-AUTHCODE'))
    logconfig = "logging_docker.json"