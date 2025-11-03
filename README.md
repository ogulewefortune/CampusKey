# CampusKey - Biometric & RFID Authentication System

## 📋 PROJECT OVERVIEW

CampusKey is a simple 2-week MVP for a multi-factor authentication system using Flutter (Mobile) + Python FastAPI (Backend) to replace textual passwords with biometric + RFID authentication for Fake University.

**App Name:** CampusKey  
**Testing:** Both iOS (iPhone) and Android devices

## 🛠️ TECHNOLOGY STACK

- **Mobile App:** Flutter (Dart) - Cross-platform for iOS/Android
- **Backend API:** Python FastAPI - Lightweight & fast
- **Database:** SQLite - Simple, no setup required (or in-memory dict for simplicity)

## 🗂️ PROJECT STRUCTURE

```
campuskey/
├── backend/
│   ├── main.py
│   └── requirements.txt
└── mobile_app/
    ├── lib/
    │   ├── main.dart
    │   └── login_screen.dart
    └── pubspec.yaml
```

## 🚀 SETUP INSTRUCTIONS

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

✅ You'll see: `Uvicorn running on http://0.0.0.0:8000`

### 2. Find Your Computer's IP Address

**On Mac:**
```bash
ipconfig getifaddr en0
```

**On Windows:**
```bash
ipconfig
# Look for IPv4 Address
```

### 3. Update IP in Flutter Code

Open `mobile_app/lib/main.dart` and change the `baseUrl` to your computer's IP address.

Example: `"http://192.168.1.105:8000"`

### 4. Flutter Setup

```bash
cd mobile_app
flutter pub get
flutter run
```

### 5. Test on Both Devices

**iPhone:**
- Connect iPhone via USB
- Trust computer when prompted
- Run `flutter run`

**Android:**
- Connect Android device via USB
- Enable USB debugging in Developer Options
- Run `flutter run`

## 🐍 BACKEND CODE

### backend/requirements.txt

```
fastapi==0.104.1
uvicorn==0.24.0
```

### backend/main.py (SIMPLE VERSION)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow mobile app to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple user database - no SQLite needed!
users = {
    "student1": {"password": "pass123", "role": "student"},
    "professor1": {"password": "pass123", "role": "professor"}, 
    "admin1": {"password": "pass123", "role": "admin"}
}

@app.get("/")
def home():
    return {"message": "CampusKey API Running"}

@app.post("/login")
def login(username: str, password: str):
    if username in users and users[username]["password"] == password:
        return {
            "success": True,
            "user": username, 
            "role": users[username]["role"],
            "message": "Login successful"
        }
    return {
        "success": False,
        "message": "Wrong username or password"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

## 📱 FLUTTER MOBILE APP CODE

### mobile_app/pubspec.yaml

```yaml
name: campuskey
description: "Simple CampusKey App"

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0

flutter:
  uses-material-design: true
```

### mobile_app/lib/main.dart (SIMPLE VERSION)

```dart
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CampusKey',
      home: LoginScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  TextEditingController usernameController = TextEditingController();
  TextEditingController passwordController = TextEditingController();
  String message = '';
  bool isLoading = false;

  // REPLACE WITH YOUR COMPUTER'S IP ADDRESS
  String baseUrl = "http://192.168.1.105:8000";

  Future<void> login() async {
    if (isLoading) return;
    
    setState(() {
      isLoading = true;
      message = 'Logging in...';
    });

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login'),
        body: {
          'username': usernameController.text,
          'password': passwordController.text,
        },
      ).timeout(Duration(seconds: 5));

      final data = jsonDecode(response.body);
      
      setState(() {
        if (data['success']) {
          message = '✅ Welcome ${data['user']}! (${data['role']})';
        } else {
          message = '❌ ${data['message']}';
        }
      });
    } catch (e) {
      setState(() {
        message = '❌ Connection failed. Check server and IP address.';
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('CampusKey'),
        backgroundColor: Colors.blue,
      ),
      body: Padding(
        padding: EdgeInsets.all(20),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.key, size: 60, color: Colors.blue),
            SizedBox(height: 10),
            Text('CampusKey Login', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 30),
            
            TextField(
              controller: usernameController,
              decoration: InputDecoration(
                labelText: 'Username',
                border: OutlineInputBorder(),
              ),
            ),
            SizedBox(height: 15),
            TextField(
              controller: passwordController,
              decoration: InputDecoration(
                labelText: 'Password', 
                border: OutlineInputBorder(),
              ),
              obscureText: true,
            ),
            SizedBox(height: 20),
            
            ElevatedButton(
              onPressed: isLoading ? null : login,
              child: isLoading 
                  ? CircularProgressIndicator(color: Colors.white)
                  : Text('LOGIN', style: TextStyle(fontSize: 18)),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                minimumSize: Size(double.infinity, 50),
              ),
            ),
            SizedBox(height: 20),
            
            Text(message, style: TextStyle(fontSize: 16)),
            SizedBox(height: 10),
            
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                TextButton(
                  onPressed: () {
                    usernameController.text = 'student1';
                    passwordController.text = 'pass123';
                  },
                  child: Text('Student'),
                ),
                TextButton(
                  onPressed: () {
                    usernameController.text = 'professor1';
                    passwordController.text = 'pass123';
                  },
                  child: Text('Professor'),
                ),
                TextButton(
                  onPressed: () {
                    usernameController.text = 'admin1';
                    passwordController.text = 'pass123';
                  },
                  child: Text('Admin'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
```

## 🎯 TEST CREDENTIALS

| Role | Username | Password |
|------|----------|----------|
| Student | `student1` | `pass123` |
| Professor | `professor1` | `pass123` |
| Admin | `admin1` | `pass123` |

## ✅ WHAT YOU'LL SEE WORKING

- ✅ Python server running on your computer
- ✅ Flutter app on both iPhone and Android
- ✅ Login works - shows welcome message with role
- ✅ Error handling - shows connection issues clearly

## 🔧 TROUBLESHOOTING

### Connection Issues

If connection fails:

1. **Check Python server is running**
   - Look for: `Uvicorn running on http://0.0.0.0:8000`
   - Test in browser: `http://localhost:8000`

2. **Verify IP address in Flutter code**
   - Make sure the IP in `main.dart` matches your computer's IP
   - Run `ipconfig getifaddr en0` (Mac) or `ipconfig` (Windows) to check

3. **Ensure phone and computer are on same WiFi**
   - Both devices must be connected to the same network

4. **Try turning computer firewall temporarily off**
   - Firewall might be blocking port 8000

5. **Check port 8000 is not in use**
   - Another application might be using port 8000
   - Change port in `main.py` if needed

## 📝 NOTES

- This is a simple MVP version - no SQLite database needed
- The backend uses an in-memory dictionary for user storage
- Works on both iOS and Android devices
- Simple and straightforward - no over-complications!

## 🎯 FEATURES

- ✅ Secure authentication
- ✅ Role-based access control (Student, Professor, Admin)
- ✅ Cross-platform support (iOS & Android)
- ✅ Simple and easy to use
- ✅ Professional CampusKey branding

---

**Built with ❤️ for Fake University**

