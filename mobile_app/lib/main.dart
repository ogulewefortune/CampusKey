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
  String baseUrl = "http://10.100.159.199:8000";

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
          message = ' Welcome ${data['user']}! (${data['role']})';
        } else {
          message = ' ${data['message']}';
        }
      });
    } catch (e) {
      setState(() {
        message = ' Connection failed. Check server and IP address.';
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
