// Dashboard/Home Screen - Main app interface after login
// This screen shows welcome info, stats, access levels, history, and verification codes
import 'package:flutter/material.dart';
import '../main.dart';
import 'profile_screen.dart';
import 'admin_panel_screen.dart';

class DashboardScreen extends StatefulWidget {
  final String username;
  final String role;
  final String token;

  const DashboardScreen({
    Key? key,
    required this.username,
    required this.role,
    required this.token,
  }) : super(key: key);

  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;

  // Mock data based on user role - Building Access
  List<Map<String, dynamic>> get _accessBuildings {
    switch (widget.role) {
      case 'admin':
        return [
          {'name': 'Main Administration', 'access': 'Full', 'time': '24/7'},
          {'name': 'Student Center', 'access': 'Full', 'time': '6 AM - 10 PM'},
          {'name': 'Library', 'access': 'Full', 'time': '7 AM - 11 PM'},
          {'name': 'Science Building', 'access': 'Full', 'time': '24/7'},
          {'name': 'Faculty Offices', 'access': 'Full', 'time': '8 AM - 6 PM'},
        ];
      case 'professor':
        return [
          {'name': 'Faculty Offices', 'access': 'Full', 'time': '8 AM - 6 PM'},
          {'name': 'Science Building', 'access': 'Full', 'time': '7 AM - 9 PM'},
          {'name': 'Library', 'access': 'Full', 'time': '7 AM - 11 PM'},
          {'name': 'Classroom Wing A', 'access': 'Limited', 'time': 'During Classes'},
        ];
      case 'student':
        return [
          {'name': 'Student Center', 'access': 'Full', 'time': '6 AM - 10 PM'},
          {'name': 'Library', 'access': 'Full', 'time': '7 AM - 11 PM'},
          {'name': 'Recreation Center', 'access': 'Full', 'time': '6 AM - 11 PM'},
          {'name': 'Classroom Wing A', 'access': 'Limited', 'time': 'During Classes'},
        ];
      default:
        return [];
    }
  }

  // Mock data based on user role - File Access Levels
  List<Map<String, dynamic>> get _fileAccess {
    switch (widget.role) {
      case 'admin':
        return [
          {'name': 'Student Records', 'level': 'Confidential', 'icon': Icons.folder_special},
          {'name': 'Financial Data', 'level': 'Restricted', 'icon': Icons.attach_money},
          {'name': 'Faculty Files', 'level': 'Confidential', 'icon': Icons.people},
          {'name': 'Research Data', 'level': 'Protected', 'icon': Icons.science},
        ];
      case 'professor':
        return [
          {'name': 'Course Materials', 'level': 'Internal', 'icon': Icons.menu_book},
          {'name': 'Student Grades', 'level': 'Confidential', 'icon': Icons.grade},
          {'name': 'Research Files', 'level': 'Protected', 'icon': Icons.science},
        ];
      case 'student':
        return [
          {'name': 'Course Materials', 'level': 'Internal', 'icon': Icons.menu_book},
          {'name': 'Personal Records', 'level': 'Private', 'icon': Icons.person},
          {'name': 'Library Resources', 'level': 'Public', 'icon': Icons.library_books},
        ];
      default:
        return [];
    }
  }

  // Mock login history data
  List<Map<String, dynamic>> _loginHistory = [
    {'date': '2024-01-15 09:30:23', 'method': 'Password', 'location': 'Campus WiFi', 'status': 'Success'},
    {'date': '2024-01-14 14:15:47', 'method': 'Biometric', 'location': 'Library', 'status': 'Success'},
    {'date': '2024-01-14 08:45:12', 'method': 'RFID', 'location': 'Main Entrance', 'status': 'Success'},
    {'date': '2024-01-13 16:20:33', 'method': 'Password', 'location': 'Off-campus', 'status': 'Failed'},
  ];

  String _currentCode = '8A3F9B';
  int _codeExpiry = 300; // 5 minutes in seconds

  @override
  void initState() {
    super.initState();
    _startCodeTimer();
  }

  void _startCodeTimer() {
    // Timer for code expiration countdown
    Future.delayed(Duration(seconds: 1), () {
      if (mounted && _codeExpiry > 0) {
        setState(() {
          _codeExpiry--;
        });
        _startCodeTimer();
      } else if (_codeExpiry == 0) {
        _generateNewCode();
      }
    });
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  // Home Tab - Welcome card, stats, quick access, recent activity
  Widget _buildHomeTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Welcome Card
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      CircleAvatar(
                        backgroundColor: Colors.blue[900],
                        radius: 30,
                        child: Text(
                          widget.username[0].toUpperCase(),
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20),
                        ),
                      ),
                      SizedBox(width: 15),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Welcome, ${widget.username}',
                              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                            ),
                            SizedBox(height: 4),
                            Container(
                              padding: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                              decoration: BoxDecoration(
                                color: _getRoleColor(widget.role),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                widget.role.toUpperCase(),
                                style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 15),
                  Divider(),
                  SizedBox(height: 10),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildStatCard('Today\'s Logins', '3', Icons.login, Colors.blue),
                      _buildStatCard('Active Sessions', '1', Icons.security, Colors.green),
                      _buildStatCard('Access Points', _accessBuildings.length.toString(), Icons.location_on, Colors.orange),
                    ],
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 20),
          // Quick Access
          Text('Quick Access', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          GridView.count(
            shrinkWrap: true,
            physics: NeverScrollableScrollPhysics(),
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            children: [
              _buildQuickAccessCard('Generate Code', Icons.qr_code, Colors.blue, () => setState(() => _selectedIndex = 3)),
              _buildQuickAccessCard('Access History', Icons.history, Colors.green, () => setState(() => _selectedIndex = 2)),
              _buildQuickAccessCard('My Profile', Icons.person, Colors.orange, _navigateToProfile),
              _buildQuickAccessCard('Security Settings', Icons.security, Colors.red, _navigateToSecurity),
            ],
          ),
          SizedBox(height: 20),
          // Recent Activity
          Text('Recent Activity', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          Card(
            child: Padding(
              padding: EdgeInsets.all(16),
              child: Column(
                children: _loginHistory.take(3).map((login) => _buildLoginHistoryItem(login)).toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // Access Control Tab - Building and File Access
  Widget _buildAccessTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Building Access', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          ..._accessBuildings.map((building) => _buildAccessCard(building)).toList(),
          SizedBox(height: 20),
          Text('File Access Levels', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          ..._fileAccess.map((file) => _buildFileAccessCard(file)).toList(),
        ],
      ),
    );
  }

  // History Tab - Complete login history
  Widget _buildHistoryTab() {
    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Login History (Last 30 Days)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          ..._loginHistory.map((login) => _buildLoginHistoryItem(login)).toList(),
        ],
      ),
    );
  }

  // Codes Tab - Verification Code Generator
  Widget _buildCodeTab() {
    String minutes = (_codeExpiry ~/ 60).toString().padLeft(2, '0');
    String seconds = (_codeExpiry % 60).toString().padLeft(2, '0');
    
    return SingleChildScrollView(
      padding: EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Verification Code Generator', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          Card(
            elevation: 4,
            child: Padding(
              padding: EdgeInsets.all(20),
              child: Column(
                children: [
                  Icon(Icons.qr_code_2, size: 80, color: Colors.blue[900]),
                  SizedBox(height: 20),
                  Text('One-Time Verification Code', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  SizedBox(height: 10),
                  Container(
                    padding: EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.blue),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _currentCode,
                      style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 2),
                    ),
                  ),
                  SizedBox(height: 15),
                  Text('Expires in: $minutes:$seconds', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                  SizedBox(height: 20),
                  ElevatedButton.icon(
                    onPressed: _generateNewCode,
                    icon: Icon(Icons.refresh),
                    label: Text('Generate New Code'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue[900],
                      padding: EdgeInsets.symmetric(vertical: 15, horizontal: 30),
                    ),
                  ),
                  SizedBox(height: 10),
                  Text(
                    'Use this code for remote login verification or when biometric/RFID is unavailable.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
          ),
          SizedBox(height: 20),
          Text('Recent Codes', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          SizedBox(height: 10),
          _buildRecentCodesList(),
        ],
      ),
    );
  }

  Color _getRoleColor(String role) {
    switch (role) {
      case 'admin': return Colors.red;
      case 'professor': return Colors.orange;
      case 'student': return Colors.blue;
      default: return Colors.grey;
    }
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 30),
        SizedBox(height: 5),
        Text(value, style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        Text(title, style: TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }

  Widget _buildQuickAccessCard(String title, IconData icon, Color color, Function onTap) {
    return Card(
      elevation: 2,
      child: InkWell(
        onTap: () => onTap(),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, color: color, size: 32),
              SizedBox(height: 8),
              Text(title, textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAccessCard(Map<String, dynamic> building) {
    return Card(
      margin: EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Icon(Icons.business, color: Colors.blue),
        title: Text(building['name']),
        subtitle: Text('Access: ${building['access']} • ${building['time']}'),
        trailing: Icon(Icons.verified, color: Colors.green),
      ),
    );
  }

  Widget _buildFileAccessCard(Map<String, dynamic> file) {
    return Card(
      margin: EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Icon(file['icon'], color: _getAccessLevelColor(file['level'])),
        title: Text(file['name']),
        subtitle: Text('Access Level: ${file['level']}'),
        trailing: _getAccessLevelIcon(file['level']),
      ),
    );
  }

  Widget _buildLoginHistoryItem(Map<String, dynamic> login) {
    return Container(
      padding: EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: Colors.grey[200]!)),
      ),
      child: Row(
        children: [
          Icon(
            login['status'] == 'Success' ? Icons.check_circle : Icons.error,
            color: login['status'] == 'Success' ? Colors.green : Colors.red,
          ),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(login['date'], style: TextStyle(fontWeight: FontWeight.bold)),
                Text('${login['method']} • ${login['location']}'),
              ],
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: login['status'] == 'Success' ? Colors.green[50] : Colors.red[50],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              login['status'],
              style: TextStyle(
                color: login['status'] == 'Success' ? Colors.green : Colors.red,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentCodesList() {
    return Card(
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            _buildCodeHistoryItem('8A3F9B', '2024-01-15 08:30', 'Used'),
            _buildCodeHistoryItem('C7E2A1', '2024-01-14 14:20', 'Expired'),
            _buildCodeHistoryItem('4D9B2F', '2024-01-13 09:15', 'Used'),
          ],
        ),
      ),
    );
  }

  Widget _buildCodeHistoryItem(String code, String date, String status) {
    return Container(
      padding: EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        border: Border(bottom: BorderSide(color: Colors.grey[200]!)),
      ),
      child: Row(
        children: [
          Icon(Icons.qr_code, color: Colors.grey),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(code, style: TextStyle(fontFamily: 'Monospace', fontWeight: FontWeight.bold)),
                Text(date, style: TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: status == 'Used' ? Colors.green[50] : Colors.orange[50],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              status,
              style: TextStyle(
                color: status == 'Used' ? Colors.green : Colors.orange,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getAccessLevelColor(String level) {
    switch (level) {
      case 'Confidential': return Colors.red;
      case 'Restricted': return Colors.orange;
      case 'Protected': return Colors.blue;
      case 'Internal': return Colors.green;
      case 'Private': return Colors.purple;
      default: return Colors.grey;
    }
  }

  Widget _getAccessLevelIcon(String level) {
    IconData icon;
    Color color = _getAccessLevelColor(level);
    
    switch (level) {
      case 'Confidential': icon = Icons.visibility_off;
      case 'Restricted': icon = Icons.lock;
      case 'Protected': icon = Icons.verified_user;
      case 'Internal': icon = Icons.person_pin;
      default: icon = Icons.public;
    }
    
    return Icon(icon, color: color);
  }

  void _generateNewCode() {
    setState(() {
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
      final random = DateTime.now().millisecondsSinceEpoch;
      _currentCode = '';
      for (int i = 0; i < 6; i++) {
        _currentCode += chars[(random + i) % chars.length];
      }
      _codeExpiry = 300; // Reset to 5 minutes
    });
  }

  void _navigateToProfile() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ProfileScreen(
          username: widget.username,
          role: widget.role,
        ),
      ),
    );
  }

  void _navigateToSecurity() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ProfileScreen(
          username: widget.username,
          role: widget.role,
        ),
      ),
    );
  }

  void _navigateToAdmin() {
    if (widget.role == 'admin') {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => AdminPanelScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('CampusKey'),
        backgroundColor: Colors.blue[900],
        elevation: 0,
        actions: [
          IconButton(
            icon: Icon(Icons.notifications),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('No new notifications')),
              );
            },
          ),
          if (widget.role == 'admin')
            IconButton(
              icon: Icon(Icons.admin_panel_settings),
              onPressed: _navigateToAdmin,
            ),
          IconButton(
            icon: Icon(Icons.logout),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => LoginScreen()),
              );
            },
          ),
        ],
      ),
      body: _getCurrentTab(),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        selectedItemColor: Colors.blue[900],
        unselectedItemColor: Colors.grey,
        items: [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.security), label: 'Access'),
          BottomNavigationBarItem(icon: Icon(Icons.history), label: 'History'),
          BottomNavigationBarItem(icon: Icon(Icons.qr_code), label: 'Codes'),
        ],
      ),
    );
  }

  Widget _getCurrentTab() {
    switch (_selectedIndex) {
      case 0: return _buildHomeTab();
      case 1: return _buildAccessTab();
      case 2: return _buildHistoryTab();
      case 3: return _buildCodeTab();
      default: return _buildHomeTab();
    }
  }
}

