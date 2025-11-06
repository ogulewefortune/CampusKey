// Profile & Security Settings Screen - User management and security preferences
import 'package:flutter/material.dart';
import 'biometric_registration_screen.dart';

class ProfileScreen extends StatefulWidget {
  final String username;
  final String role;

  const ProfileScreen({super.key, required this.username, required this.role});

  @override
  _ProfileScreenState createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _biometricEnabled = false;
  bool _twoFactorEnabled = true;
  bool _notificationsEnabled = true;
  String _currentRFIDToken = 'RFID-1234567890';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Profile & Settings'),
        backgroundColor: Colors.blue[900],
      ),
      body: ListView(
        padding: EdgeInsets.all(16),
        children: [
          // User Info Card
          Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(
                    backgroundColor: Colors.blue[900],
                    radius: 40,
                    child: Text(
                      widget.username[0].toUpperCase(),
                      style: TextStyle(color: Colors.white, fontSize: 24),
                    ),
                  ),
                  SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(widget.username, style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                        Text('${widget.username}@fakeuniversity.edu'),
                        SizedBox(height: 5),
                        Container(
                          padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                          decoration: BoxDecoration(
                            color: Colors.blue[100],
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(widget.role.toUpperCase(), style: TextStyle(fontSize: 12)),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 20),
          // Security Settings
          Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Security Settings', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  SwitchListTile(
                    title: Text('Biometric Authentication'),
                    subtitle: Text('Use Face ID/Touch ID for login'),
                    value: _biometricEnabled,
                    onChanged: (value) {
                      setState(() {
                        _biometricEnabled = value;
                        if (value) {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (context) => BiometricRegistrationScreen()),
                          );
                        }
                      });
                    },
                  ),
                  SwitchListTile(
                    title: Text('Two-Factor Authentication'),
                    subtitle: Text('Require verification code for new devices'),
                    value: _twoFactorEnabled,
                    onChanged: (value) => setState(() => _twoFactorEnabled = value),
                  ),
                  SwitchListTile(
                    title: Text('Login Notifications'),
                    subtitle: Text('Get alerts for new login attempts'),
                    value: _notificationsEnabled,
                    onChanged: (value) => setState(() => _notificationsEnabled = value),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 20),
          // RFID Management
          Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('RFID Management', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  ListTile(
                    leading: Icon(Icons.credit_card),
                    title: Text('Current RFID Token'),
                    subtitle: Text(_currentRFIDToken),
                  ),
                  ListTile(
                    leading: Icon(Icons.refresh),
                    title: Text('Generate New RFID Token'),
                    onTap: () {
                      setState(() {
                        _currentRFIDToken = 'RFID-${DateTime.now().millisecondsSinceEpoch}';
                      });
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('New RFID token generated')),
                      );
                    },
                  ),
                  ListTile(
                    leading: Icon(Icons.block, color: Colors.red),
                    title: Text('Revoke RFID Access', style: TextStyle(color: Colors.red)),
                    onTap: () {
                      showDialog(
                        context: context,
                        builder: (context) => AlertDialog(
                          title: Text('Revoke RFID Access'),
                          content: Text('Are you sure you want to revoke your RFID card access?'),
                          actions: [
                            TextButton(
                              onPressed: () => Navigator.pop(context),
                              child: Text('Cancel'),
                            ),
                            TextButton(
                              onPressed: () {
                                Navigator.pop(context);
                                setState(() {
                                  _currentRFIDToken = '';
                                });
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('RFID access revoked')),
                                );
                              },
                              child: Text('Revoke', style: TextStyle(color: Colors.red)),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 20),
          // Emergency Features
          Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Emergency Features', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  ListTile(
                    leading: Icon(Icons.emergency, color: Colors.red),
                    title: Text('Emergency Lockdown', style: TextStyle(color: Colors.red)),
                    subtitle: Text('Immediately revoke all access permissions'),
                    onTap: () {
                      _showEmergencyLockdownDialog();
                    },
                  ),
                  ListTile(
                    leading: Icon(Icons.report, color: Colors.orange),
                    title: Text('Report Security Issue'),
                    subtitle: Text('Contact campus security immediately'),
                    onTap: () {
                      _showReportDialog();
                    },
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showEmergencyLockdownDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Emergency Lockdown', style: TextStyle(color: Colors.red)),
        content: Text('This will immediately revoke ALL access permissions and log you out from all devices.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Emergency lockdown activated'),
                  backgroundColor: Colors.red,
                ),
              );
            },
            child: Text('Activate', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  void _showReportDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Report Security Issue'),
        content: Text('Contact campus security:\n\nEmergency: (555) 911\nSecurity Office: (555) 123-4567\nEmail: security@fakeuniversity.edu'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('Close'),
          ),
        ],
      ),
    );
  }
}

