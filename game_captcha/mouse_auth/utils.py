import numpy as np
from scipy import stats
import pandas as pd
import joblib
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from django.conf import settings
import os

MODEL_PATH = os.path.join(settings.BASE_DIR, 'apps/mouse_auth/ml_model/mouse_model.joblib')
FEATURE_NAMES_PATH = os.path.join(settings.BASE_DIR, 'apps/mouse_auth/ml_model/feature_names.joblib')

def extract_features(sequence):
    features = {}
    x = np.array([p[0] for p in sequence])
    y = np.array([p[1] for p in sequence])
    
    # Basic movement features
    dx = np.diff(x)
    dy = np.diff(y)
    distances = np.sqrt(dx**2 + dy**2)
    
    features['total_distance'] = np.sum(distances)
    features['straightness'] = np.sqrt((x[-1]-x[0])**2 + (y[-1]-y[0])**2) / (features['total_distance'] + 1e-6)
    
    # Velocity features
    features['mean_velocity'] = np.mean(distances)
    features['velocity_std'] = np.std(distances)
    features['max_velocity'] = np.max(distances)
    
    # Acceleration features
    if len(distances) > 1:
        accelerations = np.diff(distances)
        features['mean_acceleration'] = np.mean(accelerations)
        features['acceleration_std'] = np.std(accelerations)
    else:
        features['mean_acceleration'] = 0
        features['acceleration_std'] = 0
    
    # Angle features
    angles = np.arctan2(dy, dx)
    if len(angles) > 1:
        angle_changes = np.diff(angles)
        features['mean_angle_change'] = np.mean(np.abs(angle_changes))
        features['angle_change_std'] = np.std(angle_changes)
    else:
        features['mean_angle_change'] = 0
        features['angle_change_std'] = 0
    
    # Advanced features
    features['x_entropy'] = stats.entropy(np.histogram(x, bins=5)[0]+1e-6)
    features['y_entropy'] = stats.entropy(np.histogram(y, bins=5)[0]+1e-6)
    
    return features

def train_model():
    from .models import MouseMovementSequence
    
    # Get all training data
    sequences = MouseMovementSequence.objects.filter(
        session__is_training_data=True
    ).select_related('session')  # Only select_related to session
    
    if sequences.count() < 3:
        raise ValueError("Not enough training data available")
    
    features = []
    labels = []
    
    for seq in sequences:
        if len(seq.sequence) >= 5:
            seq_features = extract_features(seq.sequence)
            features.append(seq_features)
            
            # Works with both IntegerField and ForeignKey approaches
            if hasattr(seq.session, 'user'):  # If using ForeignKey
                labels.append(seq.session.user.id)
            else:  # If using IntegerField
                labels.append(seq.session.user_id)
    
    features_df = pd.DataFrame(features).fillna(0)
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        features_df, labels, test_size=0.2, random_state=42
    )
    
    # Train model
    model = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=5,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Save model and feature names
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(list(features_df.columns), FEATURE_NAMES_PATH)
    
    return model.score(X_test, y_test)

def verify_user_identity(user_id, movement_sequence):
    try:
        model = joblib.load(MODEL_PATH)
        feature_names = joblib.load(FEATURE_NAMES_PATH)
    except:
        raise ValueError("Model not trained yet")
    
    features = extract_features(movement_sequence)
    input_data = pd.DataFrame([features])[feature_names].fillna(0)
    
    predicted_user_id = model.predict(input_data)[0]
    confidence = np.max(model.predict_proba(input_data))
    
    return {
        'is_authentic': int(predicted_user_id == user_id),
        'confidence': float(confidence),
        'predicted_user_id': predicted_user_id
    }