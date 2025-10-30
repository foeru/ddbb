# Gradio 빵 스캔 데모

> iPhone 카메라로 빵을 스캔하는 시연용 앱

## 🎯 개요

이 앱은 학습된 YOLOv8 모델을 사용하여 iPhone Safari에서 실시간으로 빵을 인식하고 가격을 계산하는 데모 앱입니다.

## 📋 사전 준비

### 1. Python 3.12 설치 확인
```bash
python3 --version
# Python 3.12.x가 출력되어야 함
```

### 2. 학습된 모델 파일
- `best.pt` 파일이 이 폴더에 있어야 합니다
- Google Colab 학습 완료 후 다운로드한 파일

## 🚀 설치 및 실행

### 1단계: 라이브러리 설치 (Mac)
```bash
cd /Users/kyungmin/Downloads/ddbb/gradio-demo

# Python 3.12용 가상환경 생성 (선택사항)
python3 -m venv venv
source venv/bin/activate

# 라이브러리 설치
pip3 install -r requirements.txt
```

### 2단계: 모델 파일 복사
```bash
# Google Colab에서 다운로드한 best.pt를 이 폴더로 복사
cp ~/Downloads/best.pt .
```

### 3단계: 앱 실행
```bash
python3 app.py
```

출력 예시:
```
✅ 모델 로드 성공!
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://xxxxx.gradio.live

This share link expires in 72 hours.
```

## 📱 iPhone에서 접속

### 방법 1: 공개 URL 사용 (추천)
```
1. 터미널에 출력된 Public URL 복사
   예: https://xxxxx.gradio.live

2. iPhone Safari에서 접속

3. 카메라 권한 허용

4. "웹캠" 버튼 클릭 → 빵 촬영 → "스캔 시작"
```

### 방법 2: 같은 WiFi 사용 (로컬)
```
1. Mac과 iPhone을 같은 WiFi에 연결

2. Mac의 IP 주소 확인:
   시스템 설정 → 네트워크 → WiFi → IP 주소
   예: 192.168.0.10

3. iPhone Safari에서 접속:
   http://192.168.0.10:7860
```

## 🎬 사용 방법

### 실시간 카메라 모드
```
1. "웹캠" 탭 클릭
2. iPhone 카메라로 빵 트레이 촬영
3. "스캔 시작" 버튼 클릭
4. 결과 확인:
   - 왼쪽: 인식된 빵 (바운딩 박스)
   - 오른쪽: 영수증 (빵 목록 + 가격)
```

### 파일 업로드 모드
```
1. "업로드" 탭 클릭
2. 미리 찍어둔 사진 선택
3. "스캔 시작" 버튼 클릭
4. 결과 확인
```

## 🎥 발표 시연 팁

### 발표 준비 (10분 전)
```
1. Mac에서 Gradio 실행
2. iPhone에서 공개 URL 접속
3. 카메라 권한 허용
4. 테스트 촬영 1-2회
5. 빵 트레이 준비 (여러 종류 섞어서)
```

### 시연 대본
```
발표자: "이제 실제로 빵을 스캔해보겠습니다."

[iPhone 들어올림]

발표자: "iPhone Safari에서 저희 빵 스캔 시스템에 접속했습니다."

[빵 트레이 촬영]

발표자: "카메라로 빵 트레이를 촬영하고, 스캔 시작 버튼을 누르면..."

[결과 화면 표시]

발표자: "소보로빵 2개, 크로와상 1개가 인식되었고,
        총 금액은 6,100원입니다!"

[박수 👏]
```

### 조명 체크
```
✅ 밝은 곳에서 촬영
✅ 그림자 최소화
✅ 빵이 선명하게 보이도록
```

## 🐛 문제 해결

### Q1: 모델 로드 실패
```
⚠️ best.pt 파일이 없습니다. 학습 완료 후 이 폴더에 복사하세요.
```

**해결:**
```bash
# best.pt 파일을 gradio-demo/ 폴더로 복사
cp ~/Downloads/best.pt /Users/kyungmin/Downloads/ddbb/gradio-demo/
```

### Q2: iPhone 카메라 권한 없음
```
iPhone Safari에서 카메라 접근 허용
설정 → Safari → 카메라 → 허용
```

### Q3: 공개 URL 만료
```
Gradio 공개 URL은 72시간 후 만료됩니다.
앱을 다시 실행하면 새로운 URL이 생성됩니다.
```

### Q4: 빵이 인식 안 됨
```
- 조명 확인 (너무 어둡지 않은지)
- 빵이 화면에 잘 보이는지
- 카메라 초점이 맞는지
- 모델 학습이 충분했는지 (mAP > 0.85)
```

### Q5: 라이브러리 설치 오류
```bash
# pip 업그레이드
pip3 install --upgrade pip

# 라이브러리 재설치
pip3 install -r requirements.txt --force-reinstall
```

## 📊 지원 빵 종류 (10종)

| 빵 이름 | 영문명 | 가격 |
|---------|--------|------|
| 소보로빵 | soboro_bread | 1,800원 |
| 단팥빵 | red_bean_bread | 1,500원 |
| 크림빵 | cream_bread | 1,800원 |
| 버터롤 | butter_roll | 1,200원 |
| 크로와상 | croissant | 2,500원 |
| 소금빵 | salt_bread | 1,300원 |
| 모카빵 | mocha_bread | 2,000원 |
| 식빵 | white_bread | 3,500원 |
| 바게트 | baguette | 2,800원 |
| 베이글 | bagel | 2,200원 |

## 🔧 커스터마이징

### 빵 가격 변경
`app.py` 파일의 `PRICES` 딕셔너리 수정:
```python
PRICES = {
    'soboro_bread': 2000,  # 1,800원 → 2,000원으로 변경
    ...
}
```

### 인식 신뢰도 조정
`app.py` 파일의 `conf` 값 조정:
```python
results = model(image, conf=0.5)  # 0.5 = 50% 신뢰도
# 값이 높을수록 엄격함 (0.3 ~ 0.7 추천)
```

### UI 테마 변경
`app.py` 파일의 `theme` 변경:
```python
with gr.Blocks(theme=gr.themes.Soft()) as demo:
# Soft, Base, Monochrome 등 사용 가능
```

## 📸 시연 영상 촬영

### 촬영 구도
```
카메라 1: 발표자 + 스크린 (정면)
카메라 2: iPhone 화면 클로즈업
카메라 3: 빵 트레이 클로즈업
```

### 편집 순서
```
1. 발표자 소개
2. 시스템 설명
3. iPhone 화면 → 빵 촬영 → 결과 표시
4. 마무리
```

## 🎓 다음 단계

Gradio 데모 완료 후:
1. ✅ 팀원들에게 시연
2. ✅ 피드백 받기
3. ✅ 발표 리허설
4. ✅ 시연 영상 촬영

## 🌐 참고 자료

- Gradio 공식 문서: https://www.gradio.app/docs
- YOLOv8 문서: https://docs.ultralytics.com
- Python 3.12: https://www.python.org/downloads/