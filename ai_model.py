#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Willis AI 모델 아키텍처 (Neuro-T 기반)
- 논문 참고: CNN 기반 딥러닝 모델 (90% 정확도 목표)
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
import numpy as np
from typing import Tuple


class WillisNeuroModel:
    """Willis 안면 계측 AI 모델"""
    
    def __init__(self, input_shape: Tuple[int, int] = (468, 2)):
        """
        초기화
        
        Args:
            input_shape: 입력 랜드마크 shape (468개 좌표, x/y)
        """
        self.input_shape = input_shape
        self.model = self._build_model()
    
    def _build_model(self) -> keras.Model:
        """
        CNN 모델 구축 (Neuro-T 스타일)
        
        입력: 468개 랜드마크 좌표
        출력: 3개 클래스 (평균 이하 / 정상 / 평균 이상)
        """
        # 입력 레이어
        inputs = layers.Input(shape=self.input_shape, name='landmarks_input')
        
        # Flatten
        x = layers.Flatten()(inputs)
        
        # Dense layers with Batch Normalization and Dropout
        x = layers.Dense(512, activation='relu', name='dense1')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Dense(256, activation='relu', name='dense2')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Dense(128, activation='relu', name='dense3')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.2)(x)
        
        x = layers.Dense(64, activation='relu', name='dense4')(x)
        x = layers.BatchNormalization()(x)
        
        # 출력 레이어 (3-class classification)
        outputs = layers.Dense(3, activation='softmax', name='classification')(x)
        
        # 모델 생성
        model = models.Model(inputs=inputs, outputs=outputs, name='willis_neuro_model')
        
        return model
    
    def compile_model(self, learning_rate: float = 0.001):
        """모델 컴파일"""
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy', 
                    keras.metrics.Precision(name='precision'),
                    keras.metrics.Recall(name='recall')]
        )
    
    def summary(self):
        """모델 요약"""
        self.model.summary()
    
    def train(self, 
              X_train: np.ndarray, 
              y_train: np.ndarray,
              X_val: np.ndarray = None,
              y_val: np.ndarray = None,
              epochs: int = 50,
              batch_size: int = 32) -> keras.callbacks.History:
        """
        모델 학습
        
        Args:
            X_train: 학습 데이터 (n_samples, 468, 2)
            y_train: 학습 라벨 (n_samples,) - 0: 평균 이하, 1: 정상, 2: 평균 이상
            X_val: 검증 데이터
            y_val: 검증 라벨
            epochs: 에폭 수
            batch_size: 배치 크기
        
        Returns:
            학습 히스토리
        """
        # 콜백 설정
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=10,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            ),
            keras.callbacks.ModelCheckpoint(
                'data/training/best_model.keras',
                monitor='val_accuracy' if X_val is not None else 'accuracy',
                save_best_only=True
            )
        ]
        
        # 학습
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        예측
        
        Args:
            X: 입력 데이터 (n_samples, 468, 2)
        
        Returns:
            (클래스, 확률) 튜플
        """
        probabilities = self.model.predict(X)
        classes = np.argmax(probabilities, axis=1)
        return classes, probabilities
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray):
        """모델 평가"""
        results = self.model.evaluate(X_test, y_test, verbose=0)
        print("\n" + "=" * 60)
        print("모델 평가 결과")
        print("=" * 60)
        print(f"Loss: {results[0]:.4f}")
        print(f"Accuracy: {results[1]:.4f} ({results[1]*100:.1f}%)")
        print(f"Precision: {results[2]:.4f}")
        print(f"Recall: {results[3]:.4f}")
        print("=" * 60)
        
        # 논문 기준 체크 (90% 목표)
        if results[1] >= 0.90:
            print("✅ 논문 기준 달성! (90% 이상)")
        else:
            print(f"⚠️  논문 기준 미달 (목표: 90%, 현재: {results[1]*100:.1f}%)")
    
    def save(self, path: str = "data/training/willis_model.keras"):
        """모델 저장"""
        self.model.save(path)
        print(f"✅ 모델 저장: {path}")
    
    @classmethod
    def load(cls, path: str = "data/training/willis_model.keras"):
        """모델 로드"""
        instance = cls()
        instance.model = keras.models.load_model(path)
        print(f"✅ 모델 로드: {path}")
        return instance


class FeatureBasedModel:
    """특징 기반 간단한 모델 (랜드마크 대신 Willis 측정값 사용)"""
    
    def __init__(self):
        """초기화"""
        self.model = self._build_model()
    
    def _build_model(self) -> keras.Model:
        """
        간단한 MLP 모델
        
        입력: 5개 특징 (willis_ratio, pupil_to_mouth, nose_to_chin, symmetry, is_frontal)
        출력: 3개 클래스
        """
        inputs = layers.Input(shape=(5,), name='features_input')
        
        x = layers.Dense(64, activation='relu')(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        
        x = layers.Dense(32, activation='relu')(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.2)(x)
        
        x = layers.Dense(16, activation='relu')(x)
        
        outputs = layers.Dense(3, activation='softmax', name='classification')(x)
        
        model = models.Model(inputs=inputs, outputs=outputs, name='willis_feature_model')
        
        return model
    
    def compile_model(self, learning_rate: float = 0.001):
        """모델 컴파일"""
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
    
    def summary(self):
        """모델 요약"""
        self.model.summary()
    
    def train(self, X_train, y_train, X_val=None, y_val=None, epochs=100, batch_size=16):
        """모델 학습"""
        callbacks = [
            keras.callbacks.EarlyStopping(patience=15, restore_best_weights=True),
            keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=7, min_lr=1e-6)
        ]
        
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def predict(self, X):
        """예측"""
        probabilities = self.model.predict(X)
        classes = np.argmax(probabilities, axis=1)
        return classes, probabilities
    
    def evaluate(self, X_test, y_test):
        """모델 평가"""
        results = self.model.evaluate(X_test, y_test, verbose=0)
        print(f"\nTest Loss: {results[0]:.4f}")
        print(f"Test Accuracy: {results[1]:.4f} ({results[1]*100:.1f}%)")
    
    def save(self, path: str = "data/training/willis_feature_model.keras"):
        """모델 저장"""
        self.model.save(path)
        print(f"✅ 모델 저장: {path}")
    
    @classmethod
    def load(cls, path: str = "data/training/willis_feature_model.keras"):
        """모델 로드"""
        instance = cls()
        instance.model = keras.models.load_model(path)
        print(f"✅ 모델 로드: {path}")
        return instance


def demo_training():
    """데모 학습 (작은 샘플 데이터)"""
    print("=" * 60)
    print("Willis AI 모델 데모")
    print("=" * 60)
    
    # 더미 데이터 생성
    print("\n📦 더미 데이터 생성 중...")
    n_samples = 100
    
    # 랜드마크 데이터 (468개 좌표)
    X_landmarks = np.random.rand(n_samples, 468, 2)
    
    # 특징 데이터 (5개 특징)
    X_features = np.random.rand(n_samples, 5)
    X_features[:, 0] = np.random.uniform(0.8, 1.2, n_samples)  # willis_ratio
    
    # 라벨 (0: 평균 이하, 1: 정상, 2: 평균 이상)
    y = np.random.randint(0, 3, n_samples)
    
    # 분할
    split = int(0.8 * n_samples)
    X_landmarks_train, X_landmarks_val = X_landmarks[:split], X_landmarks[split:]
    X_features_train, X_features_val = X_features[:split], X_features[split:]
    y_train, y_val = y[:split], y[split:]
    
    # 1. Neuro-T 스타일 모델
    print("\n" + "=" * 60)
    print("1. Neuro-T 스타일 모델 (랜드마크 기반)")
    print("=" * 60)
    neuro_model = WillisNeuroModel()
    neuro_model.summary()
    neuro_model.compile_model()
    print("\n⚠️  실제 데이터로 학습하려면 ai_train_prepare.py 사용")
    
    # 2. 특징 기반 모델
    print("\n" + "=" * 60)
    print("2. 특징 기반 간단 모델")
    print("=" * 60)
    feature_model = FeatureBasedModel()
    feature_model.summary()
    feature_model.compile_model()
    
    print("\n🚀 특징 기반 모델 학습 시작...")
    history = feature_model.train(
        X_features_train, y_train,
        X_features_val, y_val,
        epochs=50,
        batch_size=16
    )
    
    print("\n📊 최종 성능:")
    feature_model.evaluate(X_features_val, y_val)


if __name__ == "__main__":
    demo_training()
