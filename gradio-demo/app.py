import gradio as gr
from ultralytics import YOLO
from PIL import Image
import os
import numpy as np
import cv2
from datetime import datetime
import time
import json

# 빵 가격표
PRICES = {
    'croissant': 3200,
    'salt_bread': 2800,
    'cookie': 4200,
    'eggmayo': 4500,
    'muffin': 4500,
    'pie': 4700,
    'twisted_bread': 3500
}

# 빵 이름 한글 변환
KOREAN_NAMES = {
    'croissant': '오리지널크라상',
    'salt_bread': '소금버터롤',
    'cookie': '다크초코피넛버터쿠키',
    'eggmayo': '에그마요소금버터롤',
    'muffin': '초코청크머핀',
    'pie': '호두파이(조각)',
    'twisted_bread': '츄러스꽈배기'
}

# YOLOv8 모델 로드 (모바일 최적화)
MODEL_PATH = 'best.pt'

if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH)
    print("✅ 모델 로드 성공!")

    # 모델 워밍업
    try:
        dummy_frame = np.zeros((640, 640, 3), dtype=np.uint8)
        model(dummy_frame, imgsz=640, verbose=False)
        print("✅ 모델 워밍업 완료!")
    except:
        pass
else:
    print("⚠️ best.pt 파일이 없습니다.")
    model = None


def generate_cart_html(bread_count):
    """프로덕션 레벨 장바구니 - 인터랙티브 카드 디자인"""
    if not bread_count:
        return """
        <div class='empty-cart'>
            <div class='empty-cart-icon'>
                <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
                    <circle cx="60" cy="60" r="60" fill="#F8F9FA"/>
                    <path d="M40 45L50 35L70 35L80 45L75 75H45L40 45Z" stroke="#D4A574" stroke-width="3" fill="none"/>
                    <circle cx="50" cy="82" r="4" fill="#D4A574"/>
                    <circle cx="70" cy="82" r="4" fill="#D4A574"/>
                </svg>
            </div>
            <h3 style='margin: 24px 0 12px; font-size: 22px; font-weight: 700; color: #2c3e50;'>
                장바구니가 비어있습니다
            </h3>
            <p style='font-size: 15px; color: #95a5a6; line-height: 1.6;'>
                아래 촬영 버튼을 눌러<br>빵을 인식시켜 주세요
            </p>
        </div>
        """

    items_html = []
    for idx, (bread_name, count) in enumerate(sorted(bread_count.items())):
        korean_name = KOREAN_NAMES.get(bread_name, bread_name)
        unit_price = PRICES.get(bread_name, 0)
        subtotal = unit_price * count

        items_html.append(f"""
        <div class='cart-item' style='animation: slideInRight 0.3s ease-out {idx * 0.1}s both;'>
            <div class='cart-item-header'>
                <div class='item-info'>
                    <div class='item-icon'>🥖</div>
                    <div>
                        <div class='item-name'>{korean_name}</div>
                        <div class='item-price-unit'>{unit_price:,}원</div>
                    </div>
                </div>
                <div class='item-quantity'>
                    <span class='quantity-badge'>×{count}</span>
                </div>
            </div>
            <div class='cart-item-footer'>
                <div class='item-subtotal'>{subtotal:,}원</div>
            </div>
        </div>
        """)

    return f"""
    <div class='cart-container'>
        <div class='cart-scroll'>
            {''.join(items_html)}
        </div>
    </div>
    """


def generate_total_html(bread_count):
    """프로덕션 레벨 결제 정보 패널"""
    if not bread_count:
        return """
        <div class='total-panel-empty'>
            <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="24" fill="#F0F0F0"/>
                <text x="24" y="30" text-anchor="middle" font-size="20" fill="#999">₩</text>
            </svg>
            <p style='margin: 16px 0 0; font-size: 16px; color: #999; font-weight: 500;'>
                상품을 추가하면 금액이 계산됩니다
            </p>
        </div>
        """

    total_price = sum(PRICES.get(name, 0) * count for name, count in bread_count.items())
    total_count = sum(bread_count.values())

    return f"""
    <div class='total-panel'>
        <div class='total-row'>
            <span class='total-label'>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style="vertical-align: middle; margin-right: 8px;">
                    <rect x="3" y="3" width="14" height="14" rx="2" stroke="#7f8c8d" stroke-width="1.5" fill="none"/>
                    <path d="M7 10L9 12L13 8" stroke="#7f8c8d" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
                총 수량
            </span>
            <span class='total-value'>{total_count}개</span>
        </div>
        <div class='total-divider'></div>
        <div class='total-row-main'>
            <span class='total-label-main'>총 결제금액</span>
            <div class='total-price-wrapper'>
                <span class='total-price'>{total_price:,}</span>
                <span class='total-currency'>원</span>
            </div>
        </div>
    </div>
    """


def process_bread_image(frame, current_bread_count):
    """빵 인식 및 장바구니 업데이트"""
    if model is None or frame is None:
        return None, current_bread_count, generate_cart_html(current_bread_count), generate_total_html(current_bread_count)

    try:
        # 이미지 전처리
        h, w = frame.shape[:2]

        if max(h, w) > 1280:
            scale = 1280 / max(h, w)
            new_w = int(w * scale)
            new_h = int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # YOLO 추론
        results = model(frame, imgsz=640, conf=0.1, iou=0.45, verbose=False, augment=True)

        # Confidence 70% 이상만 필터링
        CONFIDENCE_THRESHOLD = 0.70

        filtered_boxes = []
        for box in results[0].boxes:
            if float(box.conf) >= CONFIDENCE_THRESHOLD:
                filtered_boxes.append(box)

        # 바운딩 박스가 그려진 이미지
        result_image = results[0].plot()

        # 빵 카운트
        new_items = {}
        for box in filtered_boxes:
            class_id = int(box.cls)
            class_name = model.names[class_id]
            new_items[class_name] = new_items.get(class_name, 0) + 1

        # 기존 장바구니에 추가
        for bread_name, count in new_items.items():
            current_bread_count[bread_name] = current_bread_count.get(bread_name, 0) + count

        # 메모리 정리
        del results

        # HTML 생성
        cart_html = generate_cart_html(current_bread_count)
        total_html = generate_total_html(current_bread_count)

        return result_image, current_bread_count, cart_html, total_html

    except Exception as e:
        print(f"오류 발생: {str(e)}")
        return None, current_bread_count, generate_cart_html(current_bread_count), generate_total_html(current_bread_count)


def on_payment_click(bread_count):
    """결제 버튼 클릭 처리"""
    if not bread_count:
        return bread_count, generate_cart_html(bread_count), generate_total_html(bread_count), gr.update(visible=False)

    # 결제 처리 시뮬레이션 (2초 대기)
    time.sleep(2)

    # 장바구니 초기화
    empty_cart = {}
    return empty_cart, generate_cart_html(empty_cart), generate_total_html(empty_cart), gr.update(value="결제가 완료되었습니다! 🎉", visible=True)


def on_reset_click():
    """초기화 버튼"""
    empty_cart = {}
    return None, empty_cart, generate_cart_html(empty_cart), generate_total_html(empty_cart), gr.update(visible=False)


# CSS - 프로덕션 레벨 UI/UX 디자인
css = """
/* ============================================
   글로벌 리셋 & 베이스 스타일
   ============================================ */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

:root {
    --primary: #D4A574;
    --primary-dark: #B8935E;
    --primary-light: #E8D4B8;
    --background: #FAFAF8;
    --surface: #FFFFFF;
    --surface-secondary: #FFF8F0;
    --text-primary: #1A1A1A;
    --text-secondary: #6B7280;
    --border: #E5E7EB;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
    --shadow-md: 0 4px 12px rgba(0,0,0,0.1);
    --shadow-lg: 0 10px 40px rgba(0,0,0,0.12);
    --radius-sm: 12px;
    --radius-md: 16px;
    --radius-lg: 24px;
}

body, .gradio-container {
    background: var(--background) !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif !important;
    color: var(--text-primary) !important;
}

.gradio-container {
    max-width: 100vw !important;
    padding: 0 !important;
}

/* ============================================
   헤더 스타일
   ============================================ */
#kiosk-header {
    background: var(--surface);
    box-shadow: var(--shadow-sm);
    margin-bottom: 0;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    position: sticky;
    top: 0;
    z-index: 100;
}

/* ============================================
   메인 컨텐츠 영역
   ============================================ */
#main-content {
    padding: 32px 40px;
    min-height: calc(100vh - 250px);
    gap: 24px;
}

#camera-section {
    background: var(--surface);
    border-radius: var(--radius-lg);
    padding: 28px;
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

#camera-section:hover {
    box-shadow: var(--shadow-lg);
}

#cart-section {
    background: var(--surface-secondary);
    border-radius: var(--radius-lg);
    padding: 28px;
    box-shadow: var(--shadow-md);
    display: flex;
    flex-direction: column;
}

/* ============================================
   장바구니 스타일
   ============================================ */
.empty-cart {
    height: 500px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
}

.empty-cart-icon {
    animation: float 3s ease-in-out infinite;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

.cart-container {
    flex: 1;
    overflow: hidden;
}

.cart-scroll {
    height: 500px;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 12px;
}

.cart-item {
    background: var(--surface);
    border-radius: var(--radius-md);
    padding: 20px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
}

.cart-item:hover {
    transform: translateX(4px) scale(1.01);
    box-shadow: var(--shadow-md);
    border-color: var(--primary-light);
}

.cart-item:active {
    transform: translateX(2px) scale(0.99);
}

.cart-item-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 14px;
}

.item-info {
    display: flex;
    align-items: center;
    gap: 14px;
}

.item-icon {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, var(--primary-light) 0%, var(--surface-secondary) 100%);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
}

.item-name {
    font-size: 17px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
    line-height: 1.3;
}

.item-price-unit {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 500;
}

.quantity-badge {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 8px 18px;
    border-radius: 20px;
    font-size: 16px;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(212, 165, 116, 0.3);
}

.cart-item-footer {
    display: flex;
    justify-content: flex-end;
    padding-top: 14px;
    border-top: 1px solid var(--border);
}

.item-subtotal {
    font-size: 22px;
    font-weight: 800;
    color: var(--primary-dark);
    letter-spacing: -0.5px;
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

/* ============================================
   결제 정보 패널
   ============================================ */
#bottom-bar {
    background: var(--surface);
    box-shadow: 0 -4px 20px rgba(0,0,0,0.08);
    padding: 28px 40px;
    border-top: 1px solid var(--border);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}

.total-panel-empty {
    text-align: center;
    padding: 32px;
    background: var(--surface);
    border-radius: var(--radius-lg);
    border: 2px dashed var(--border);
}

.total-panel {
    background: var(--surface);
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    box-shadow: var(--shadow-md);
    border: 1px solid var(--border);
}

.total-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.total-label {
    font-size: 16px;
    color: var(--text-secondary);
    font-weight: 600;
    display: flex;
    align-items: center;
}

.total-value {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
}

.total-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 20px 0;
}

.total-row-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.total-label-main {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
}

.total-price-wrapper {
    display: flex;
    align-items: baseline;
    gap: 6px;
}

.total-price {
    font-size: 36px;
    font-weight: 900;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -1px;
}

.total-currency {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-secondary);
}

/* ============================================
   버튼 스타일
   ============================================ */
#payment-button {
    width: 100%;
    padding: 24px 32px !important;
    font-size: 22px !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius-md) !important;
    cursor: pointer !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 20px rgba(212, 165, 116, 0.35) !important;
    position: relative !important;
    overflow: hidden !important;
}

#payment-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.5s;
}

#payment-button:hover::before {
    left: 100%;
}

#payment-button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 30px rgba(212, 165, 116, 0.45) !important;
}

#payment-button:active {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(212, 165, 116, 0.35) !important;
}

#reset-button {
    width: 100%;
    padding: 18px 32px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    background: var(--surface) !important;
    color: var(--text-secondary) !important;
    border: 2px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin-top: 14px !important;
}

#reset-button:hover {
    background: var(--surface-secondary) !important;
    border-color: var(--primary-light) !important;
    color: var(--primary-dark) !important;
    transform: translateY(-1px) !important;
}

#reset-button:active {
    transform: translateY(0px) !important;
}

/* ============================================
   스크롤바 커스텀
   ============================================ */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: var(--surface-secondary);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--primary) 0%, var(--primary-dark) 100%);
    border-radius: 10px;
    border: 2px solid var(--surface-secondary);
}

::-webkit-scrollbar-thumb:hover {
    background: var(--primary-dark);
}

/* ============================================
   반응형 디자인
   ============================================ */
@media (max-width: 1024px) {
    #main-content {
        padding: 20px;
        flex-direction: column;
    }

    #camera-section, #cart-section {
        width: 100% !important;
        padding: 20px;
    }

    .cart-scroll {
        height: 400px;
    }

    #bottom-bar {
        padding: 20px;
    }

    .total-price {
        font-size: 28px;
    }
}

@media (max-width: 768px) {
    .item-name {
        font-size: 15px;
    }

    .item-subtotal {
        font-size: 18px;
    }

    #payment-button {
        font-size: 18px !important;
        padding: 20px !important;
    }
}

/* ============================================
   로딩 & 애니메이션
   ============================================ */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.loading {
    animation: pulse 1.5s ease-in-out infinite;
}
"""

# Gradio 인터페이스
with gr.Blocks(css=css, title="DDBB Bakery 키오스크", theme=gr.themes.Soft()) as demo:

    # 상태 저장
    bread_count_state = gr.State({})

    # 프로덕션 레벨 헤더
    with gr.Row(elem_id="kiosk-header"):
        gr.HTML("""
            <div style='
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 28px 40px;
            '>
                <div style='display: flex; align-items: center; gap: 20px;'>
                    <div style='
                        width: 56px;
                        height: 56px;
                        background: linear-gradient(135deg, #D4A574 0%, #B8935E 100%);
                        border-radius: 16px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 32px;
                        box-shadow: 0 4px 12px rgba(212, 165, 116, 0.3);
                    '>
                        🥖
                    </div>
                    <div>
                        <div style='
                            font-size: 32px;
                            font-weight: 800;
                            color: #1A1A1A;
                            letter-spacing: -0.5px;
                            margin-bottom: 4px;
                        '>
                            DDBB Bakery
                        </div>
                        <div style='
                            font-size: 14px;
                            color: #6B7280;
                            font-weight: 600;
                            letter-spacing: 0.3px;
                        '>
                            AI-Powered Smart POS System
                        </div>
                    </div>
                </div>
                <div style='
                    text-align: right;
                    padding: 12px 20px;
                    background: #F8F9FA;
                    border-radius: 12px;
                    border: 1px solid #E5E7EB;
                '>
                    <div style='
                        font-size: 13px;
                        color: #6B7280;
                        font-weight: 600;
                        margin-bottom: 4px;
                    '>
                        OPEN
                    </div>
                    <div style='
                        font-size: 16px;
                        color: #1A1A1A;
                        font-weight: 700;
                    '>
                        """ + datetime.now().strftime('%Y.%m.%d') + """
                    </div>
                </div>
            </div>
        """)

    # 메인 컨텐츠 (2단 구조)
    with gr.Row(elem_id="main-content"):
        # 왼쪽: 카메라 영역
        with gr.Column(scale=6, elem_id="camera-section"):
            gr.HTML("""
                <div style='
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    margin-bottom: 24px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #F0F0F0;
                '>
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                        <rect x="4" y="8" width="24" height="18" rx="3" stroke="#D4A574" stroke-width="2.5" fill="none"/>
                        <circle cx="16" cy="17" r="4" stroke="#D4A574" stroke-width="2.5" fill="none"/>
                        <circle cx="23" cy="12" r="1.5" fill="#D4A574"/>
                    </svg>
                    <div>
                        <div style='font-size: 22px; font-weight: 800; color: #1A1A1A; letter-spacing: -0.3px;'>
                            제품 촬영
                        </div>
                        <div style='font-size: 13px; color: #6B7280; font-weight: 500; margin-top: 2px;'>
                            빵을 카메라에 담아주세요
                        </div>
                    </div>
                </div>
            """)

            # 이미지 입력
            image_input = gr.Image(
                sources=["upload"],
                type="numpy",
                label="",
                height=380
            )

            # 촬영 버튼 (프로덕션 레벨)
            gr.HTML("""
                <div style='margin-top: 24px;'>
                    <label for='kiosk-file-upload' class='capture-button'>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" style="vertical-align: middle; margin-right: 10px;">
                            <circle cx="12" cy="12" r="10" stroke="white" stroke-width="2" fill="none"/>
                            <circle cx="12" cy="12" r="4" fill="white"/>
                        </svg>
                        빵 촬영하기
                    </label>
                    <input
                        type='file'
                        id='kiosk-file-upload'
                        accept='image/*'
                        capture='environment'
                        style='display: none;'
                    />
                </div>
                <style>
                    .capture-button {
                        display: block;
                        width: 100%;
                        padding: 22px 32px;
                        font-size: 20px;
                        font-weight: 700;
                        text-align: center;
                        background: linear-gradient(135deg, #D4A574 0%, #B8935E 100%);
                        color: white;
                        border-radius: 16px;
                        cursor: pointer;
                        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        box-shadow: 0 4px 15px rgba(212, 165, 116, 0.35);
                        border: none;
                        user-select: none;
                        position: relative;
                        overflow: hidden;
                    }
                    .capture-button::before {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
                        transition: left 0.5s;
                    }
                    .capture-button:hover {
                        transform: translateY(-3px);
                        box-shadow: 0 8px 25px rgba(212, 165, 116, 0.45);
                    }
                    .capture-button:hover::before {
                        left: 100%;
                    }
                    .capture-button:active {
                        transform: translateY(-1px);
                        box-shadow: 0 4px 15px rgba(212, 165, 116, 0.35);
                    }
                </style>
            """)

            # 인식 결과 이미지
            result_image = gr.Image(
                label="인식 결과",
                height=380
            )

        # 오른쪽: 장바구니 영역
        with gr.Column(scale=4, elem_id="cart-section"):
            gr.HTML("""
                <div style='
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 24px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #E8D4B8;
                '>
                    <div style='display: flex; align-items: center; gap: 12px;'>
                        <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                            <path d="M8 10L10 8H22L24 10L23 22H9L8 10Z" stroke="#D4A574" stroke-width="2.5" fill="none"/>
                            <circle cx="13" cy="26" r="2" fill="#D4A574"/>
                            <circle cx="21" cy="26" r="2" fill="#D4A574"/>
                            <line x1="11" y1="14" x2="21" y2="14" stroke="#D4A574" stroke-width="2" stroke-linecap="round"/>
                        </svg>
                        <div>
                            <div style='font-size: 22px; font-weight: 800; color: #1A1A1A; letter-spacing: -0.3px;'>
                                장바구니
                            </div>
                            <div style='font-size: 13px; color: #6B7280; font-weight: 500; margin-top: 2px;'>
                                선택된 제품 목록
                            </div>
                        </div>
                    </div>
                </div>
            """)

            # 장바구니 리스트
            cart_html = gr.HTML(generate_cart_html({}))

    # 하단: 합계 및 결제 버튼
    with gr.Row(elem_id="bottom-bar"):
        with gr.Column(scale=7):
            total_html = gr.HTML(generate_total_html({}))

        with gr.Column(scale=3):
            payment_btn = gr.Button(
                "💳 결제하기",
                size="lg",
                elem_id="payment-button"
            )
            reset_btn = gr.Button(
                "🔄 초기화",
                size="sm",
                elem_id="reset-button"
            )
            payment_status = gr.Textbox(label="", visible=False)

    # 이벤트 핸들러
    image_input.change(
        fn=process_bread_image,
        inputs=[image_input, bread_count_state],
        outputs=[result_image, bread_count_state, cart_html, total_html]
    )

    payment_btn.click(
        fn=on_payment_click,
        inputs=bread_count_state,
        outputs=[bread_count_state, cart_html, total_html, payment_status]
    )

    reset_btn.click(
        fn=on_reset_click,
        outputs=[image_input, bread_count_state, cart_html, total_html, payment_status]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True
    )
