# VolumeControl - Gesture-Based Volume Controller

## Overview
**VolumeControl** is a macOS Python project that allows you to **control your system volume using hand gestures** via your webcam. It leverages **MediaPipe** for hand tracking and **OpenCV** for real-time video capture.  

- **Thumb-Index Gesture:** Adjust volume by moving the distance between your thumb and index finger.  
- **Closed Fist:** Mute or unmute the system.  
- **Calibration:** Set minimum and maximum distances for personalized control.  

This project is **resume-ready** and demonstrates skills in **Computer Vision, Python, AI/ML, and real-time gesture interaction**.

---

## Features
- Real-time hand tracking using **MediaPipe**  
- Smooth volume adjustment with **numpy averaging**  
- Mute/unmute gesture detection  
- Calibration for minimum and maximum thumb-index distance  
- On-screen UI showing current volume level  

## Installation

### **Requirements**
- macOS
- Python 3.10
- Webcam

### **Steps**
1. Clone the repository:

bash
git clone https://github.com/<USERNAME>/VolumeControl.git
cd VolumeControl
