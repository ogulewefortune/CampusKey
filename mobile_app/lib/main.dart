// Import Flutter's Material Design library - provides UI components (buttons, text fields, etc.)
import 'package:flutter/material.dart';
// BACKEND IMPORTS COMMENTED OUT FOR UI TESTING
// Import Dart's convert library - used for JSON encoding/decoding
// import 'dart:convert';
// Import HTTP package - used for making API calls to the backend server
// import 'package:http/http.dart' as http;
// Import SplashScreen widget - the initial loading screen with logo
import 'screens/splash_screen.dart';
// Import DashboardScreen widget - main app interface after login
import 'screens/dashboard_screen.dart';
// Import screens for alternative login methods
import 'screens/face_login_screen.dart';
import 'screens/rfid_simulation_screen.dart';
import 'screens/password_reset_flow.dart';

// Main entry point of the Flutter application
// This function runs when the app starts and initializes MyApp widget
void main() => runApp(MyApp());

// MyApp class - Root widget of the application
// StatelessWidget means this widget doesn't change its state during runtime
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // Override the build method - required for all widgets
  // This method describes how to display this widget
  @override
  Widget build(BuildContext context) {
    // MaterialApp is the root widget that configures the entire app
    return MaterialApp(
      title: 'CampusKey', // App title displayed in task switcher
      home: SplashScreen(), // First screen to show when app launches
      debugShowCheckedModeBanner: false, // Hide the "DEBUG" banner in top-right corner
    );
  }
}

// LoginScreen class - Widget for user authentication
// StatefulWidget allows this widget to change its state (e.g., user input, loading)
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  // Override createState - creates the state object that manages this widget
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

// _LoginScreenState class - Manages the state of LoginScreen
// The underscore prefix makes it private to this file
class _LoginScreenState extends State<LoginScreen> {
  // TextEditingController for username field - manages the text input
  TextEditingController usernameController = TextEditingController();
  // TextEditingController for password field - manages the password input
  TextEditingController passwordController = TextEditingController();
  // String to store and display messages (success/error messages)
  String message = '';
  // Boolean flag to track if login request is in progress (prevents multiple clicks)
  bool isLoading = false;

  // REPLACE WITH YOUR COMPUTER'S IP ADDRESS
  // Base URL for the backend API server (COMMENTED OUT FOR UI TESTING)
  // This should match your computer's IP address running the FastAPI server
  // String baseUrl = "http://10.100.159.199:8000";

  // Async function to handle login process
  // async allows this function to wait for network requests
  Future<void> login() async {
    // If already loading, prevent multiple simultaneous login attempts
    if (isLoading) return;
    
    // setState updates the widget's state and triggers a rebuild
    setState(() {
      isLoading = true; // Set loading flag to true (shows loading indicator)
      message = 'Logging in...'; // Display loading message to user
    });

    // BACKEND CALLS COMMENTED OUT - USING MOCK DATA FOR UI TESTING
    // try-catch block handles errors during API call
    // try {
    //   // Make HTTP POST request to login endpoint
    //   final response = await http.post(
    //     Uri.parse('$baseUrl/login'), // Construct full URL for login endpoint
    //     body: {
    //       'username': usernameController.text, // Get username from text field
    //       'password': passwordController.text, // Get password from text field
    //     },
    //   ).timeout(Duration(seconds: 5)); // Set 5 second timeout for request

    //   // Decode JSON response from server to Dart Map
    //   final data = jsonDecode(response.body);
      
    //   // Update UI based on server response
    //   setState(() {
    //     // Check if login was successful
    //     if (data['success']) {
    //       message = ' Welcome ${data['user']}! (${data['role']})'; // Show welcome message
    //       // Navigate to home screen after successful login
    //       // pushReplacement replaces current screen (can't go back to login)
    //       Navigator.pushReplacement(
    //         context, // Current widget's context (required for navigation)
    //         MaterialPageRoute(
    //           // Builder function creates the DashboardScreen widget
    //           builder: (context) => DashboardScreen(
    //             username: data['user'], // Pass username from API response
    //             role: data['role'], // Pass user role from API response
    //             token: data['token'] ?? '', // Pass token if available
    //           ),
    //         ),
    //       );
    //     } else {
    //       // If login failed, show error message from server
    //       message = ' ${data['message']}';
    //     }
    //   });
    // } catch (e) {
    //   // Handle any errors (network failure, timeout, etc.)
    //   setState(() {
    //     message = ' Connection failed. Check server and IP address.'; // Show connection error
    //   });
    // } finally {
    //   // Always execute this block, whether success or error
    //   setState(() {
    //     isLoading = false; // Reset loading flag to false
    //   });
    // }

    // MOCK DATA FOR UI TESTING - Simulate successful login
    await Future.delayed(Duration(seconds: 1)); // Simulate network delay
    
    setState(() {
      isLoading = false;
      
      // Determine role based on username
      String role = 'student';
      if (usernameController.text.contains('professor')) {
        role = 'professor';
      } else if (usernameController.text.contains('admin')) {
        role = 'admin';
      }
      
      message = ' Welcome ${usernameController.text}! ($role)';
      
      // Navigate to dashboard with mock data
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(
          builder: (context) => DashboardScreen(
            username: usernameController.text.isEmpty ? 'student1' : usernameController.text,
            role: role,
            token: 'mock_token_${DateTime.now().millisecondsSinceEpoch}',
          ),
        ),
      );
    });
  }

  // Override build method - defines the UI structure of LoginScreen
  @override
  Widget build(BuildContext context) {
    // Scaffold provides basic app structure (app bar, body, etc.)
    return Scaffold(
      // AppBar - top bar of the screen
      appBar: AppBar(
        title: Text('CampusKey'), // App title in the bar
        backgroundColor: Colors.blue, // Blue background color
      ),
      // Body - main content area of the screen
      body: Padding(
        padding: EdgeInsets.all(20), // Add 20 pixels padding on all sides
        // Column widget arranges children vertically
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center, // Center content vertically
          children: [
            // Key icon - visual branding element
            Icon(Icons.key, size: 60, color: Colors.blue),
            SizedBox(height: 10), // Empty space 10 pixels tall
            // Login title text
            Text('CampusKey Login', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            SizedBox(height: 30), // Empty space 30 pixels tall
            
            // Username text input field
            TextField(
              controller: usernameController, // Connect to username controller
              decoration: InputDecoration(
                labelText: 'Username', // Label text above/below field
                border: OutlineInputBorder(), // Border style around field
              ),
            ),
            SizedBox(height: 15), // Empty space 15 pixels tall
            // Password text input field
            TextField(
              controller: passwordController, // Connect to password controller
              decoration: InputDecoration(
                labelText: 'Password', // Label text above/below field
                border: OutlineInputBorder(), // Border style around field
              ),
              obscureText: true, // Hide password characters (show dots instead)
            ),
            SizedBox(height: 10), // Empty space 10 pixels tall
            // Forgot Password button
            Align(
              alignment: Alignment.centerRight,
              child: TextButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => PasswordResetFlowScreen()),
                  );
                },
                child: Text('Forgot Password?'),
              ),
            ),
            SizedBox(height: 20), // Empty space 20 pixels tall
            
            // Login button
            ElevatedButton(
              onPressed: isLoading ? null : login, // Show text if not loading
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue, // Blue button background
                minimumSize: Size(double.infinity, 50), // Full width, 50 pixels tall
              ), // Disable if loading, otherwise call login()
              child: isLoading 
                  ? CircularProgressIndicator(color: Colors.white) // Show spinner if loading
                  : Text('LOGIN', style: TextStyle(fontSize: 18)),
            ),
            SizedBox(height: 10), // Empty space 10 pixels tall
            
            // Divider with "OR" text
            Row(
              children: [
                Expanded(child: Divider()),
                Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Text('OR', style: TextStyle(color: Colors.grey)),
                ),
                Expanded(child: Divider()),
              ],
            ),
            SizedBox(height: 10), // Empty space 10 pixels tall
            
            // Face ID Login Button
            OutlinedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => FaceLoginScreen()),
                );
              },
              icon: Icon(Icons.face),
              label: Text('Login with Face ID'),
              style: OutlinedButton.styleFrom(
                minimumSize: Size(double.infinity, 50),
                side: BorderSide(color: Colors.blue),
              ),
            ),
            SizedBox(height: 10), // Empty space 10 pixels tall
            
            // RFID Card Login Button
            OutlinedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => RFIDSimulationScreen()),
                );
              },
              icon: Icon(Icons.credit_card),
              label: Text('Tap RFID Card'),
              style: OutlinedButton.styleFrom(
                minimumSize: Size(double.infinity, 50),
                side: BorderSide(color: Colors.blue),
              ),
            ),
            SizedBox(height: 20), // Empty space 20 pixels tall
            Text(message, style: TextStyle(fontSize: 16)),
            SizedBox(height: 10), // Empty space 10 pixels tall
            
            // Row widget arranges children horizontally
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly, // Distribute buttons evenly
              children: [
                // Student quick-fill button
                TextButton(
                  onPressed: () {
                    // Auto-fill username and password for student account
                    usernameController.text = 'student1';
                    passwordController.text = 'pass123';
                  },
                  child: Text('Student'), // Button label
                ),
                // Professor quick-fill button
                TextButton(
                  onPressed: () {
                    // Auto-fill username and password for professor account
                    usernameController.text = 'professor1';
                    passwordController.text = 'pass123';
                  },
                  child: Text('Professor'), // Button label
                ),
                // Admin quick-fill button
                TextButton(
                  onPressed: () {
                    // Auto-fill username and password for admin account
                    usernameController.text = 'admin1';
                    passwordController.text = 'pass123';
                  },
                  child: Text('Admin'), // Button label
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
