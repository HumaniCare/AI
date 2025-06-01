import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sentence_transformers import SentenceTransformer


def predict(sample_path):
    # (가정) 미리 정의된 함수/변수
    # get_features(path): (486,) 벡터 반환
    # speech_to_text(path): STT → 문자열 반환
    # boundary_enhanced_focal_loss: 커스텀 손실
    # emotion_labels: ['angry','sadness','happiness','fear','disgust','surprise','neutral']
    # model_path, sample_path: 경로 문자열

    # 1) WAV 파일 리스트
    sample_wav_list = [
        sample_path + "/jg_sadness_1.wav",
        sample_path + "/jg_sadness_2.wav",
        sample_path + "/jg_sadness_3.wav",
        sample_path + "/jg_sadness_4.wav",
        sample_path + "/jg_sadness_5.wav"
    ]

    # 2) 오디오 특징 평균 풀링
    all_feats = np.stack([get_features(p) for p in sample_wav_list], axis=0)  # (5,486)
    pooled_feats = all_feats.mean(axis=0)  # (486,)

    # 3) 모델 입력 형태 맞추기
    audio_input = pooled_feats[np.newaxis, :, np.newaxis]  # (1,486,1)

    # 4) 전체 텍스트 STT → 하나의 문장으로 결합
    texts = [speech_to_text(p) for p in sample_wav_list]
    full_text = " . ".join(texts)

    # 5) 텍스트 임베딩
    embedding_model = SentenceTransformer('jhgan/ko-sbert-multitask')
    text_vec = embedding_model.encode([full_text])[0]  # (768,)
    text_input = text_vec[np.newaxis, :]  # (1,768)

    # 6) 모델 로드 및 예측
    model = load_model(model_path, custom_objects={
        'boundary_enhanced_focal_loss': boundary_enhanced_focal_loss
    })
    prediction = model.predict([audio_input, text_input])  # (1,7)
    pred_percent = prediction[0] * 100  # (7,)

    # 7) 콘솔에 출력
    for lbl, p in zip(emotion_labels, pred_percent):
        print(f"{lbl}: {p:.2f}%")
    top_idx = np.argmax(pred_percent)
    print(f"\n최종 예측 감정: {emotion_labels[top_idx]}")

    # 8) 가로 막대그래프 시각화
    colors = ['#e74c3c', '#3498db', '#f1c40f', '#e67e22', '#9b59b6', '#1abc9c', '#95a5a6']

    plt.figure(figsize=(10, 6))
    bars = plt.barh(emotion_labels, pred_percent, color=colors, alpha=0.85)

    plt.title('Emotion Probability Distribution', fontsize=18, weight='bold', pad=15)
    plt.xlabel('Probability (%)', fontsize=14)
    plt.xlim(0, pred_percent.max() + 10)
    plt.grid(axis='x', linestyle='--', alpha=0.6)

    for bar, p in zip(bars, pred_percent):
        plt.text(p + 1, bar.get_y() + bar.get_height() / 2,
                 f'{p:.1f}%', va='center', fontsize=12, weight='bold', color='#333')

    plt.yticks(fontsize=13, weight='bold')
    plt.tight_layout()

    # 이미지 파일로 저장
    plt.savefig('emotion_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
