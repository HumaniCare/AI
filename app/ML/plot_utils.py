# 그래프 그리기
import os
from datetime import datetime

from matplotlib import pyplot as plt
from app.service.s3Service import upload_to_s3_png

colors = ['#e74c3c', '#3498db', '#f1c40f', '#e67e22', '#9b59b6', '#1abc9c', '#95a5a6']
emotion_labels = ['angry', 'sadness', 'happiness', 'fear', 'disgust', 'surprise', 'neutral']
BASE_DIR = "/home/team4/Desktop/capstone/AI/app/emotion_png"


def save_plot(predictions_percent):
    plt.figure(figsize=(10, 6))
    bars = plt.barh(emotion_labels, predictions_percent, color=colors, alpha=0.85)

    plt.title('Emotion Probability Distribution', fontsize=20, weight='bold', pad=15)
    plt.xlabel('Probability (%)', fontsize=14)
    plt.xlim(0, max(predictions_percent) + 10)
    plt.grid(axis='x', linestyle='--', alpha=0.6)

    for bar, percent in zip(bars, predictions_percent):
        width = bar.get_width()
        plt.text(width + 0.8, bar.get_y() + bar.get_height() / 2, f'{percent:.1f}%', va='center', fontsize=13,
                 weight='bold', color='#333')

    plt.yticks(fontsize=14, weight='bold')
    plt.tight_layout()

    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{date_str}"
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
    local_path = os.path.join(BASE_DIR, f"{filename}_emotion_distribution.png")
    # 이미지 파일로 저장
    plt.savefig(local_path, dpi=300, bbox_inches='tight')
    plt.show()

    return local_path


def get_s3_png_url(local_path):
    return upload_to_s3_png(local_path)
