# 💻 자동 건강상태 자가진단 - Version 2

[자동 건강상태 자가진단](https://autocovid.tech) 서비스의 오픈소스 입니다.

코로나 자가진단 API 래핑은 [hcskr](https://github.com/331leo/hcskr_python) 프로젝트에서 진행하며, 이 저장소에서는 해당 프로젝트를 이용한 웹서비스를 개발합니다.

### 🔨 작동방식

- 전반적으로 Python, Sanic(Flask) 기반으로 작동합니다.
- 데이터베이스는 MongoDB를 사용합니다.
- 웹페이지에서 입력한 정보를 바탕으로 자가진단 로그인 시도, 결과 반환합니다.
- 자가진단 로그인에 성공한 경우 DB에 유저 정보를 암호화해 저장합니다.
- Aiocron 을 이용해 월~금 7:00AM 마다 저장된 정보들을 바탕으로 코로나 자가진단 수행합니다.

### 🚀 실행하기

이 프로젝트는 Docker를 활용해 배포환경을 구축하였습니다.

docker을 이용해 이 소스코드를 실행시킬수 있습니다.

```shell
docker-compose -f docker-compose-withdb.yml up
```

- MongoDB를 포함한 환경에서 열리며, 32768번 포트에서 web(api) 서버가 열리고 37017포트에 mongodb가 실행됩니다.

### ⚙️ 설정

MongoDB와 web(api)서버를 자동으로 설정해주는 위의 `docker-compose-withdb` 를 사용하지 않는경우, 
`src/config.py` 의 내용을 수정해야 합니다.

```python
#로컬환경
mongo_host = "MongoDB 호스트네임(예: db.example.com)"
mongo_port = 27017 #MongoDB 포트
authcode = "authcode" #수동 자가진단시 인증 코드
logconfig = "logging_local.json" #나머지는 건들이지 마세요
```

### 📝 로깅

위의 `docker-compose-withdb` 를 사용하는경우, `./logs` 에 웹사이트 사용기록(등록, 해제), 자가진단 수행기록이 로깅됩니다.

위의 도커파일을 사용하지 않고, 그냥 실행하는 경우엔 `src/logs` 에 로깅됩니다.

### 📚 라이센스

- 만약 이 소스코드를 이용하는경우, 이메일: support@leok.kr 또는 Github Issues 에 사용한 프로젝트의 주소를 남겨주시고,
  GPL v3 라이센스에 따라 소스코드를 공개하셔야 합니다.

