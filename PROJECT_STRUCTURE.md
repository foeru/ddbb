# 🥖 DDBB Bakery POS - 프로젝트 구조

## 📁 디렉토리 설명

### ✅ 사용 중 (Main Projects)

```
fullstack-pos/              # 🚀 메인 프로젝트 (FastAPI + React)
├── backend/               # Python FastAPI 백엔드
│   ├── main.py           # API 엔드포인트
│   ├── models.py         # YOLO 모델
│   ├── best.pt           # AI 모델 파일
│   └── venv/             # Python 가상환경
└── frontend/             # React TypeScript 프론트엔드
    ├── src/              # 소스 코드
    ├── node_modules/     # npm 패키지
    └── package.json      # 의존성

gradio-demo/               # 📦 Gradio 버전 (레거시)
├── app.py                # Gradio 앱 (작동 중)
├── best.pt               # AI 모델 파일
└── venv/                 # Python 가상환경

data/                      # 📊 학습 데이터
├── train/                # 학습용 이미지
├── valid/                # 검증용 이미지
└── README.md             # 데이터셋 설명
```

### ⚠️ 사용 안 함 (Deprecated/Unused)

```
build/                     # Gradle 빌드 결과 (불필요)
src/                       # Java 소스? (불필요)
.gradle/                   # Gradle 캐시 (불필요)
python-api/                # 비어있음 (불필요)
gradle/, gradlew*          # Gradle 관련 (불필요)
.idea/                     # IntelliJ 설정 (불필요)
```

### 📝 문서

```
COLAB_TRAINING_GUIDE.md    # Colab 학습 가이드
ROBOFLOW_GUIDE.md          # Roboflow 데이터셋 가이드
README.md                  # 프로젝트 메인 설명 (작성 필요)
```

---

## 🚀 실행 방법

### 1️⃣ FastAPI + React (추천)
```bash
# 백엔드
cd fullstack-pos/backend
source venv/bin/activate
python3 main.py

# 프론트엔드 (새 터미널)
cd fullstack-pos/frontend
npm install
npm run dev
```

### 2️⃣ Gradio 버전 (레거시)
```bash
cd gradio-demo
source venv/bin/activate
python3 app.py
```

---

## 🧹 정리 제안

### 삭제해도 되는 것들
- `build/`
- `src/` (Java 관련)
- `.gradle/`
- `gradle/`, `gradlew*`
- `.idea/`
- `python-api/`
- `build.gradle`, `settings.gradle`
- `HELP.md` (Spring Boot 기본 파일)

### 유지해야 할 것들
- `fullstack-pos/` ✅ 메인
- `gradio-demo/` ✅ 백업용
- `data/` ✅ 학습 데이터
- `COLAB_TRAINING_GUIDE.md` ✅
- `ROBOFLOW_GUIDE.md` ✅
- `.git/` ✅ Git 히스토리
- `.gitignore`, `.gitattributes` ✅

---

## 📊 프로젝트 히스토리

1. **Spring Boot 프로젝트** (초기, 사용 중단)
   - Java 기반
   - Gradle 빌드 시스템

2. **Gradio 버전** (중간)
   - Python 올인원
   - 빠른 프로토타입

3. **FastAPI + React** (현재, 메인)
   - 프로덕션 레벨
   - 풀스택 분리 아키텍처

---

## 🎯 권장 구조 (정리 후)

```
ddbb/
├── fullstack-pos/        # 메인 프로젝트
├── gradio-demo/          # 레거시 (참고용)
├── data/                 # 학습 데이터
├── docs/                 # 문서 (새로 생성)
│   ├── COLAB_TRAINING_GUIDE.md
│   └── ROBOFLOW_GUIDE.md
├── .git/                 # Git
├── .gitignore
└── README.md             # 프로젝트 메인 설명
```
