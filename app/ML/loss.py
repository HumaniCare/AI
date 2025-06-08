import tensorflow as tf


# 1. Boundary-Enhanced Focal Loss 구현 (소수 클래스 식별 강화)
def boundary_enhanced_focal_loss(y_true, y_pred, gamma=2.0, margin=0.3):
    y_pred = tf.clip_by_value(y_pred, 1e-7, 1.0 - 1e-7)

    # 하드 샘플 마이닝 (낮은 확률로 예측된 샘플 식별)
    correct_prob = tf.reduce_sum(y_true * y_pred, axis=-1)
    hard_mask = tf.cast(tf.less(correct_prob, margin), tf.float32)

    # 클래스별 가중치 계산 (소수 클래스에 더 높은 가중치)
    effective_counts = tf.reduce_sum(y_true, axis=0)
    alpha = 1.0 / (effective_counts + 1e-7)
    alpha = alpha / tf.reduce_sum(alpha)

    # 소수 클래스 추가 가중치 부여 (surprise, neutral)
    class_boost = tf.constant([1.0, 0.5, 1.0, 1.0, 1.0, 2.5, 5.0], dtype=tf.float32)
    alpha = alpha * class_boost

    # Focal Loss 계산
    cross_entropy = -y_true * tf.math.log(y_pred)
    focal_weight = tf.pow(1.0 - y_pred, gamma)

    # 하드 샘플에 추가 가중치 부여
    sample_weight = 1.0 + hard_mask * 2.0
    loss = sample_weight[:, tf.newaxis] * alpha * focal_weight * cross_entropy

    return tf.reduce_sum(loss)
