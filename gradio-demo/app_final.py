import gradio as gr
from ultralytics import YOLO
from PIL import Image
import os

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

# YOLOv8 모델 로드
MODEL_PATH = 'best.pt'

if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH)
    print("✅ 모델 로드 성공!")
else:
    print("⚠️ best.pt 파일이 없습니다.")
    model = None


def scan_bread(image):
    """빵 이미지를 받아서 종류와 개수를 감지"""
    if model is None:
        return None, "❌ 모델 파일(best.pt)이 없습니다."

    if image is None:
        return None, "📷 이미지를 업로드해주세요."

    try:
        # YOLO 모델로 예측
        results = model(image, conf=0.5)
        result_image = results[0].plot()
        result_image = Image.fromarray(result_image)

        # 감지된 빵 카운트
        bread_count = {}
        for box in results[0].boxes:
            class_id = int(box.cls)
            class_name = model.names[class_id]
            bread_count[class_name] = bread_count.get(class_name, 0) + 1

        if len(bread_count) == 0:
            return result_image, "<div style='text-align:center;padding:50px;'>❌ 빵이 감지되지 않았습니다</div>"

        # 영수증 생성
        total_price = 0
        total_count = 0
        receipt_html = ["<div style='background:white;padding:30px;border-radius:12px;'>"]
        receipt_html.append("<h2 style='text-align:center;'>🥖 DDBB Bakery</h2>")

        for bread_name, count in sorted(bread_count.items()):
            korean_name = KOREAN_NAMES.get(bread_name, bread_name)
            unit_price = PRICES.get(bread_name, 0)
            subtotal = unit_price * count
            total_price += subtotal
            total_count += count

            receipt_html.append(f"""
                <div style='padding:10px 0;border-bottom:1px solid #eee;'>
                    <div style='font-weight:600;'>{korean_name}</div>
                    <div style='color:#666;'>{unit_price:,}원 × {count}개 = {subtotal:,}원</div>
                </div>
            """)

        receipt_html.append(f"""
            <div style='margin-top:20px;padding-top:20px;border-top:2px solid #333;font-size:20px;font-weight:bold;'>
                총 {total_count}개: {total_price:,}원
            </div>
        """)
        receipt_html.append("</div>")

        return result_image, "\n".join(receipt_html)

    except Exception as e:
        return None, f"❌ 오류: {str(e)}"


# CSS
css = """
.upload-box {
    border: 3px dashed #4CAF50;
    border-radius: 16px;
    padding: 40px;
    text-align: center;
    background: #f9f9f9;
    min-height: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.camera-input {
    display: block;
    width: 100%;
    max-width: 400px;
    padding: 20px;
    font-size: 18px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    margin: 20px auto;
}

.camera-input::file-selector-button {
    display: none;
}
"""

# Gradio 인터페이스
with gr.Blocks(css=css, title="🥖 DDBB 빵 POS") as demo:
    gr.Markdown("# 🥖 DDBB Bakery POS\n### AI-Powered Bread Recognition")

    with gr.Row():
        with gr.Column():
            gr.Markdown("## 📷 빵 촬영")

            # 큰 카메라 버튼 HTML
            gr.HTML("""
                <div class="upload-box">
                    <div style="font-size: 60px; margin-bottom: 20px;">📸</div>
                    <h3 style="margin-bottom: 10px;">빵 사진 촬영</h3>
                    <p style="color: #666; margin-bottom: 20px;">아래 버튼을 눌러 후면 카메라로 촬영하세요</p>
                    <input
                        type="file"
                        accept="image/*"
                        capture="environment"
                        id="cameraInput"
                        class="camera-input"
                        style="width: 100%; max-width: 400px; padding: 20px; font-size: 18px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 12px; cursor: pointer;"
                    />
                </div>

                <script>
                document.getElementById('cameraInput').addEventListener('change', function(e) {
                    if (e.target.files && e.target.files[0]) {
                        const file = e.target.files[0];
                        const reader = new FileReader();

                        reader.onload = function(event) {
                            // Gradio Image 컴포넌트 찾기
                            const imageInput = document.querySelector('#image-upload input[type="file"]');
                            if (imageInput) {
                                // 파일 전달
                                const dataTransfer = new DataTransfer();
                                dataTransfer.items.add(file);
                                imageInput.files = dataTransfer.files;
                                imageInput.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        };

                        reader.readAsDataURL(file);
                    }
                });
                </script>
            """)

            # Gradio Image (숨김)
            image_input = gr.Image(
                label="",
                sources=["upload"],
                type="pil",
                visible=True,
                elem_id="image-upload",
                height=300
            )

            scan_btn = gr.Button("🔍 스캔 시작", size="lg")
            result_image = gr.Image(label="인식 결과", height=300)

        with gr.Column():
            gr.Markdown("## 🧾 영수증")
            receipt = gr.HTML("""
                <div style='text-align:center;padding:80px 20px;color:#999;'>
                    빵을 촬영하고<br>스캔 버튼을 눌러주세요
                </div>
            """)

    # 스캔 버튼 클릭 시
    scan_btn.click(
        fn=scan_bread,
        inputs=image_input,
        outputs=[result_image, receipt]
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        debug=True
    )
