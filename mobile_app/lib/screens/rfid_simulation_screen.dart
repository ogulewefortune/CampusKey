// RFID Simulation Screen - Simulate RFID card tapping for login
import 'package:flutter/material.dart';
import 'dashboard_screen.dart';

class RFIDSimulationScreen extends StatefulWidget {
  @override
  _RFIDSimulationScreenState createState() => _RFIDSimulationScreenState();
}

class _RFIDSimulationScreenState extends State<RFIDSimulationScreen> {
  bool _isScanning = false;
  String _rfidToken = '';
  final TextEditingController _manualTokenController = TextEditingController();

  Future<void> _simulateRFIDTap() async {
    setState(() {
      _isScanning = true;
      _rfidToken = '';
    });

    // Simulate RFID card reading
    await Future.delayed(Duration(seconds: 2));

    // Generate a mock RFID token
    setState(() {
      _rfidToken = 'RFID-${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}';
      _isScanning = false;
    });

    // Simulate successful login after short delay
    await Future.delayed(Duration(seconds: 1));

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => DashboardScreen(
          username: 'user',
          role: 'student',
          token: _rfidToken,
        ),
      ),
    );
  }

  void _submitManualToken() {
    if (_manualTokenController.text.isNotEmpty) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => DashboardScreen(
            username: 'user',
            role: 'student',
            token: _manualTokenController.text,
          ),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('RFID Card Login'),
        backgroundColor: Colors.blue[900],
      ),
      body: Padding(
        padding: EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.credit_card, size: 100, color: Colors.blue[900]),
            SizedBox(height: 20),
            Text(
              'Tap Your RFID Card',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 10),
            Text(
              'Hold your campus card near the reader',
              style: TextStyle(color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 40),
            Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: _isScanning ? Colors.green : Colors.blue,
                  width: 3,
                ),
              ),
              child: _isScanning
                  ? Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 20),
                        Text('Reading card...'),
                      ],
                    )
                  : Icon(Icons.contactless, size: 80, color: Colors.grey[400]),
            ),
            if (_rfidToken.isNotEmpty) ...[
              SizedBox(height: 20),
              Container(
                padding: EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green[50],
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  'Card Detected: $_rfidToken',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ],
            SizedBox(height: 40),
            ElevatedButton.icon(
              onPressed: _isScanning ? null : _simulateRFIDTap,
              icon: Icon(Icons.credit_card),
              label: Text(_isScanning ? 'Scanning...' : 'Tap to Simulate'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue[900],
                padding: EdgeInsets.symmetric(horizontal: 30, vertical: 15),
                minimumSize: Size(double.infinity, 50),
              ),
            ),
            SizedBox(height: 20),
            Divider(),
            SizedBox(height: 20),
            Text('Or Enter RFID Token Manually'),
            SizedBox(height: 10),
            TextField(
              controller: _manualTokenController,
              decoration: InputDecoration(
                labelText: 'RFID Token',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.edit),
              ),
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _submitManualToken,
              child: Text('Submit Token'),
              style: ElevatedButton.styleFrom(
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

