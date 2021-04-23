import os

#로컬환경
mongo_host = "localhost"
mongo_port = 27017
authcode = "authcode"
logconfig = "logging_local.json"
google_gtag = "G-GOOGLE_GTAG"
#도커환경
if os.environ.get('DOCKER-MONGO-HOST'):
    mongo_host = str(os.environ.get('DOCKER-MONGO-HOST'))
    mongo_port = int(os.environ.get('DOCKER-MONGO-PORT'))
    authcode = str(os.environ.get('DOCKER-AUTHCODE'))
    google_gtag = str(os.environ.get("DOCKER-GOOGLE-GTAG"))
    logconfig = "logging_docker.json"