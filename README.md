# Drowsiness Detection System

![Python](https://img.shields.io/badge/Python-3.x-blue)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green)
![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey)

A comprehensive driver safety system that combines computer vision-based drowsiness detection with ECG anomaly detection using deep learning techniques.

## 📋 Overview

This project implements a multi-faceted approach to driver safety by combining real-time drowsiness detection with ECG monitoring. The system utilizes computer vision for facial feature analysis and CNN-based autoencoders for ECG anomaly detection, providing a robust solution for preventing fatigue-related accidents.

## 🎯 Project Goals

- Implement real-time drowsiness detection using computer vision
- Develop CNN-based autoencoder for ECG anomaly detection
- Create a secure user authentication system
- Provide comprehensive visualization of system performance
- Ensure robust and reliable operation in real-world conditions

## 📊 Key Features

### Drowsiness Detection
- Real-time facial feature analysis
- Eye state monitoring
- Head pose estimation
- Priority-based alert system
- Minimal hardware requirements

### ECG Analysis
- CNN-based autoencoder implementation
- Multiple loss function support:
  - Mean Squared Error (MSE)
  - Huber loss
  - Mean Absolute Error (MAE)
  - Cosine Similarity
- MIT-BIH Arrhythmia Database integration
- Comprehensive visualization tools

### Security Features
- Multi-factor authentication (MFA)
- CAPTCHA implementation
- Secure password reset mechanism
- Rate limiting
- Database security with hashed passwords

## 🛠️ Technologies Used

- Python 3.x
- TensorFlow for deep learning
- OpenCV for computer vision
- Flask for web interface
- SQLite for database management
- Matplotlib for visualization
- NumPy for numerical operations

## 📈 Project Structure

1. **Drowsiness Detection Module**
   - Facial feature detection
   - Eye state analysis
   - Alert system implementation

2. **ECG Analysis Module**
   - CNN autoencoder architecture
   - Multiple loss function implementation
   - Data preprocessing pipeline

3. **User Authentication System**
   - MFA implementation
   - CAPTCHA integration
   - Password management
   - Rate limiting

4. **Database Management**
   - User data storage
   - Admin management
   - Comment system

## 💻 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/drowsiness-detection.git
cd drowsiness-detection
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python database_init.py
```

4. Start the application:
```bash
python app.py
```

Access the system at `http://localhost:5000`

## 🔍 Key Findings

- Real-time drowsiness detection with high accuracy
- Effective ECG anomaly detection using CNN autoencoders
- Comparative analysis of different loss functions
- Secure user authentication system
- Comprehensive visualization of system performance

## 📊 Visualization

The project generates detailed visualizations including:
- Sample plots for each loss function
- Actual vs. reconstructed ECG data
- Performance metrics and comparisons
- System operation statistics

## 👤 Author

Mert Ali Celik

## 🙏 Acknowledgments

- MIT-BIH Arrhythmia Database for ECG data
- Open-source computer vision community
- Deep learning research community
- Contributors and testers
