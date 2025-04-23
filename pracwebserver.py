from http.server import BaseHTTPRequestHandler, HTTPServer  # 기본 HTTP 서버 기능 import
from urllib.parse import urlparse, parse_qsl                # URL 쿼리 파싱용 라이브러리 import

hostName = "0.0.0.0"         # 외부 기기도 접속 가능하게 모든 IP 바인딩
serverPort = 8000            # 사용할 포트 번호 (브라우저에선 :8000)

# 요청 처리 클래스 정의 (GET, POST 처리용)
class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):  # GET 요청이 들어왔을 때 호출됨
        temperature = None
        humidity = None
        self.send_response(200)                           # 200 OK 응답 코드 전송
        self.send_header("Content-type", "text/html")     # 응답 헤더 설정 (HTML로 보냄)
        self.end_headers()                                # 헤더 전송 완료
        # ex) "http://172.30.1.65:8000/?temparature=30" c언어 코드에서 이렇게 url 설정하면 
        # ex) "http://172.30.1.66:8000/?temparature=30&humidity=50"
        qs = urlparse(self.path).query                    # URL에서 ? 이후의 쿼리 문자열 추출
        if len(qs) > 0:                                   # 쿼리 문자열이 있다면
            print(parse_qsl(qs))                          # 쿼리를 리스트 형태로 출력
            for q in parse_qsl(qs):                       # 각 쿼리 파라미터 순회
                if q[0] == "temparature": 
                    temperature = q[1]                # 'temparature'라는 키가 있다면
                    print("temparature is", q[1])         # 값 출력
                if q[0] == "humidity": 
                    humidity = q[1]                   # 'humidity'라는 키가 있다면
                    print("humidity is", q[1])            # 값 출력
        self.wfile.write(bytes('{"status":"ok"}', 'utf-8'))   # JSON 형식 응답 전송

        response = f"""
        <html>
        <body>
            <h1>Sensor Data Received</h1>
            <p>Temperature: {temperature if temperature else 'N/A'}</p>
            <p>Humidity: {humidity if humidity else 'N/A'}</p>
        </body>
        </html>
        """
    # HTML 본문 작성 (브라우저로 보여짐)
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body><p>This is an example web server.</p></body></html>", "utf-8"))

    def do_POST(self):  # POST 요청 처리
        self.send_response(200)                            # 200 OK 응답 코드
        self.send_header("Content-type", "application/json")  # JSON 응답 헤더
        self.end_headers()                                 # 헤더 전송 완료

        if self.path == '/':                               # 경로가 루트("/")일 경우
            self.wfile.write(bytes('{"status":"ng"}', "utf-8"))  # 'ng' 응답 (비정상 or 미사용 경로)
        else:
            try:
                content_length = int(self.headers['Content-Length'])   # 본문 길이 읽기
                post_data = self.rfile.read(content_length)            # 본문 데이터 수신
                print(post_data)                                       # 수신 데이터 콘솔 출력

                self.wfile.write(bytes('{"status":"ok"}', "utf-8"))    # 성공 응답 전송

                safe_path = "." + self.path.replace("..", "")          # 경로 보안 처리
                with open(safe_path, "w", encoding="utf-8") as f:      # 파일로 저장
                    f.write(post_data.decode("utf-8"))                 # 텍스트로 디코딩 후 저장

            except Exception as e:
                print("Error handling POST:", e)                       # 예외 출력
                self.wfile.write(bytes('{"status":"error"}', "utf-8")) # 에러 응답 전송

# 서버 인스턴스 생성 및 실행
webServer = HTTPServer((hostName, serverPort), MyServer)   # 서버 객체 생성
print("Server started http://%s:%s" % (hostName, serverPort))  # 서버 시작 메시지

try:
    webServer.serve_forever()  # 서버 루프 시작 (중단될 때까지 계속 실행)
except KeyboardInterrupt:
    pass                       # Ctrl+C로 종료하면 에러 없이 빠져나옴

webServer.server_close()       # 서버 종료
print("Server stopped.")       # 종료 메시지 출력
