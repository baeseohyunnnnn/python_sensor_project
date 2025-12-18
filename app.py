from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# =========================================================================
# 1. 임계값 설정 (상태 판단 기준)
# =========================================================================
HIGH_TEMP_THRESHOLD = 28.0  # 28도 이상이면 고온 경고
LOW_TEMP_THRESHOLD = 10.0   # 10도 미만이면 저온 경고
HIGH_HUM_THRESHOLD = 75.0   # 75% 이상이면 고습 경고

# 수동으로 기록된 데이터를 저장할 전역 리스트
manual_records = []

# =========================================================================
# 2. 상태를 판단하는 핵심 함수
# =========================================================================
def get_status(temperature, humidity):
    """온도와 습도 값을 받아 상태 문자열을 반환합니다."""
    try:
        temp = float(temperature)
        hum = float(humidity)
    except ValueError:
        return "데이터 오류"
    
    alert_parts = []
    
    # 온도 판단
    if temp >= HIGH_TEMP_THRESHOLD:
        alert_parts.append("고온 경고")
    elif temp < LOW_TEMP_THRESHOLD:
        alert_parts.append("저온 경고")
        
    # 습도 판단
    if hum >= HIGH_HUM_THRESHOLD:
        alert_parts.append("고습 경고")
        
    # 최종 상태 결정
    if alert_parts:
        # 경고가 여러 개일 경우 콤마로 연결 (예: "고온 경고, 고습 경고")
        return ", ".join(alert_parts)
    else:
        return "정상 범위"


# =========================================================================
# 3. 라우트 함수 정의
# =========================================================================

# 메인 모니터링 대시보드 (GET /)
@app.route('/')
def monitor():
    global manual_records
    
    # 최신 기록이 먼저 보이도록 역순으로 복사하여 템플릿에 전달
    latest_manual_records = manual_records[::-1] 

    return render_template('monitor.html', 
                           HIGH_TEMP_THRESHOLD=HIGH_TEMP_THRESHOLD,
                           LOW_TEMP_THRESHOLD=LOW_TEMP_THRESHOLD,
                           HIGH_HUM_THRESHOLD=HIGH_HUM_THRESHOLD,
                           manual_records=latest_manual_records)

# 수동 데이터 입력 폼 페이지 (GET /add)
@app.route('/add')
def add_data_form():
    return render_template('add_data.html')

# 수동 데이터 제출 및 처리 (POST /submit_data)
@app.route('/submit_data', methods=['POST'])
def submit_data():
    global manual_records
    
    # 폼에서 데이터 추출
    temperature = request.form.get('temperature')
    humidity = request.form.get('humidity')
    location = request.form.get('location')
    
    # 상태 판단 함수 호출
    alert_status = get_status(temperature, humidity)
    
    # 새 기록 생성 및 저장
    new_record = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'temperature': float(temperature),
        'humidity': float(humidity),
        'location': location,
        'alert_status': alert_status 
    }
    manual_records.append(new_record)
    
    # 메인 모니터링 페이지로 리다이렉트
    return redirect(url_for('monitor'))


# 실시간 데이터 API (시뮬레이션용) - 대시보드의 카드에 표시되는 데이터
@app.route('/data')
def get_data():
    current_temp = 25.0
    current_hum = 55.0
    
    # 시뮬레이션 데이터도 상태 판단
    current_status = get_status(current_temp, current_hum) 
    
    return jsonify({
        'temperature': current_temp,
        'humidity': current_hum,
        'status': current_status
    })


if __name__ == '__main__':
    # 🚨 서버 재시작 필수!
    app.run(debug=True)