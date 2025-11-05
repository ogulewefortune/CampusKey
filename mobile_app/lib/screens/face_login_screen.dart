// Face Login Screen - Alternative login method using facial recognition
import 'package:flutter/material.dart';
import 'dashboard_screen.dart';

class FaceLoginScreen extends StatefulWidget {
  @override
  _FaceLoginScreenState createState() => _FaceLoginScreenState();
}

class _FaceLoginScreenState extends State<FaceLoginScreen> {
  bool _isScanning = false;
  bool _isProcessing = false;
  String _statusMessage = 'Position your face in front of the camera';

  Future<void> _scanFace() async {
    setState(() {
      _isScanning = true;
      _isProcessing = true;
      _statusMessage = 'Scanning face...';
    });

    // Simulate face recognition process
    await Future.delayed(Duration(seconds: 2));

    setState(() {
      _isProcessing = false;
      _statusMessage = 'Face recognized! Logging in...';
    });

    // Simulate successful login
    await Future.delayed(Duration(seconds: 1));

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => DashboardScreen(
          username: 'user',
          role: 'student',
          token: 'face_token',
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Face ID Login'),
        backgroundColor: Colors.blue[900],
      ),
      body: Center(
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Camera preview placeholder
              Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  color: Colors.grey[200],
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: Colors.blue, width: 3),
                ),
                child: _isScanning
                    ? (_isProcessing
                        ? CircularProgressIndicator()
                        : Icon(Icons.face, size: 120, color: Colors.green))
                    : Icon(Icons.camera_alt, size: 80, color: Colors.grey[600]),
              ),
              SizedBox(height: 30),
              Text(
                _statusMessage,
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 40),
              ElevatedButton.icon(
                onPressed: _isScanning ? null : _scanFace,
                icon: Icon(Icons.face),
                label: Text(_isScanning ? 'Scanning...' : 'Start Face Scan'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blue[900],
                  padding: EdgeInsets.symmetric(horizontal: 30, vertical: 15),
                ),
              ),
              SizedBox(height: 20),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: Text('Cancel'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

