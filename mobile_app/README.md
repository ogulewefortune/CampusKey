# mobile_app

A new Flutter project.

## Getting Started

This project is a starting point for a Flutter application.

Splash Screen 
    ↓
Login Screen 
    ↓ (multiple paths)
    ├── Traditional Login → Dashboard
    ├── Face Login → Face Scan → Dashboard  
    ├── RFID Login → RFID Simulation → Dashboard
    └── Forgot Password → Password Reset Flow → Login Screen

Dashboard (Bottom Navigation)
    ├── Home Tab (default)
    ├── Access Control Tab
    ├── History Tab  
    └── Codes Tab

Side Menu/Navigation Drawer
    ├── Profile & Settings
    ├── Biometric Registration
    ├── RFID Management
    └── Admin Panel (if admin)
A few resources to get you started if this is your first Flutter project:

- [Lab: Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Cookbook: Useful Flutter samples](https://docs.flutter.dev/cookbook)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.
