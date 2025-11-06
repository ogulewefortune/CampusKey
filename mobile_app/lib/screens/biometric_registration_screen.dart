// Biometric Registration Screen - Register face for biometric login
import 'package:flutter/material.dart';

class BiometricRegistrationScreen extends StatefulWidget {
  const BiometricRegistrationScreen({super.key});

  @override
  _BiometricRegistrationScreenState createState() => _BiometricRegistrationScreenState();
}

class _BiometricRegistrationScreenState extends State<BiometricRegistrationScreen> {
  bool _isCapturing = false;
  bool _isProcessing = false;
  int _captureStep = 0; // 0: Front, 1: Left, 2: Right
  String _statusMessage = 'Position your face in the center';

  final List<String> _captureInstructions = [
    'Look straight ahead',
    'Turn your head slightly left',
    'Turn your head slightly right',
  ];

  Future<void> _captureFace() async {
    setState(() {
      _isCapturing = true;
      _isProcessing = true;
      _statusMessage = 'Capturing face...';
    });

    await Future.delayed(Duration(seconds: 2));

    setState(() {
      _isProcessing = false;
      _statusMessage = 'Face captured!';
    });

    await Future.delayed(Duration(seconds: 1));

    if (_captureStep < 2) {
      setState(() {
        _captureStep++;
        _isCapturing = false;
        _statusMessage = _captureInstructions[_captureStep];
      });
    } else {
      // All captures complete
      _completeRegistration();
    }
  }

  void _completeRegistration() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Registration Complete'),
        content: Text('Your face has been successfully registered for biometric login.'),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Biometric Registration'),
        backgroundColor: Colors.blue[900],
      ),
      body: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          children: [
            // Progress indicator
            Row(
              children: List.generate(3, (index) => Expanded(
                child: Container(
                  height: 4,
                  margin: EdgeInsets.symmetric(horizontal: 4),
                  decoration: BoxDecoration(
                    color: index <= _captureStep ? Colors.blue : Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              )),
            ),
            SizedBox(height: 20),
            Text(
              'Step ${_captureStep + 1} of 3',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 40),
            // Camera preview placeholder
            Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(20),
                border: Border.all(color: Colors.blue, width: 3),
              ),
              child: _isCapturing
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
            SizedBox(height: 10),
            Text(
              _captureInstructions[_captureStep],
              style: TextStyle(color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 40),
            ElevatedButton.icon(
              onPressed: _isCapturing ? null : _captureFace,
              icon: Icon(Icons.camera_alt),
              label: Text(_isCapturing ? 'Processing...' : 'Capture Face'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[900],
                padding: EdgeInsets.symmetric(horizontal: 30, vertical: 15),
                minimumSize: Size(double.infinity, 50),
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
    );
  }
}

