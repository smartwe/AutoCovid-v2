FROM ubuntu:20.04

# /app 디렉토리 생성, 사용
RUN mkdir -p /app
WORKDIR /app
ADD . /app

# 파이썬 설치
RUN apt-get -y update &&\
 apt-get install -y python3 python3-pip

# 필요 모듈 설치
RUN pip3 install -r src/requirements.txt

# ENV 설정
ENV DOCKER-MONGO-HOST=localhost
ENV DOCKER-MONGO-PORT=27017
ENV DOCKER-AUTHCODE=authcode

# 포트열기
EXPOSE 8080

# 실행시 자동으로 서버 실행
CMD [ "python3 /app/src/api.py" ]