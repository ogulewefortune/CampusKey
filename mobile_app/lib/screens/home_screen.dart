// Import Flutter's Material Design library - provides UI components
import 'package:flutter/material.dart';

// HomeScreen class - Screen displayed after successful login
// StatelessWidget because this screen doesn't change its own state
// It receives username and role as parameters (passed from LoginScreen)
class HomeScreen extends StatelessWidget {
  // final keyword means these values can't be changed after object creation
  final String username; // Stores the logged-in user's username
  final String role; // Stores the logged-in user's role (student/professor/admin)

  // Constructor - creates HomeScreen widget with required username and role
  // const keyword allows this widget to be created at compile-time (performance optimization)
  const HomeScreen({
    Key? key, // Optional key parameter for widget identification
    required this.username, // Required parameter - username must be provided
    required this.role, // Required parameter - role must be provided
  }) : super(key: key); // Call parent constructor with key

  // Override build method - defines the UI structure of HomeScreen
  @override
  Widget build(BuildContext context) {
    // Scaffold provides basic app structure (app bar, body, etc.)
    return Scaffold(
      // AppBar - top bar of the screen
      appBar: AppBar(
        title: Text('CampusKey - Home'), // Title displayed in app bar
        backgroundColor: Colors.blue, // Blue background color for app bar
      ),
      // Body - main content area of the screen
      body: Padding(
        padding: EdgeInsets.all(20), // Add 20 pixels padding on all sides
        // Column widget arranges children vertically
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center, // Center content vertically
          children: [
            // Home icon - visual element representing home screen
            Icon(Icons.home, size: 60, color: Colors.blue),
            SizedBox(height: 20), // Empty space 20 pixels tall (spacing between icon and text)
            // Welcome message with username
            // String interpolation ($username) inserts the username value
            Text(
              'Welcome, $username!', // Display personalized welcome message
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold), // Large, bold text
            ),
            SizedBox(height: 10), // Empty space 10 pixels tall (spacing between welcome and role)
            // User role display
            Text(
              'Role: $role', // Display user's role (student/professor/admin)
              style: TextStyle(fontSize: 18, color: Colors.grey[600]), // Medium, grey text
            ),
            SizedBox(height: 40), // Empty space 40 pixels tall (spacing before button)
            // Logout button
            ElevatedButton(
              onPressed: () {
                // Navigator.pop removes current screen and goes back to previous screen
                // In this case, returns to LoginScreen (since we used pushReplacement)
                Navigator.pop(context); // Go back to login screen
              },
              child: Text('Logout'), // Button label text
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red, // Red button background (indicates logout action)
                minimumSize: Size(double.infinity, 50), // Full width, 50 pixels tall
              ),
            ),
          ],
        ),
      ),
    );
  }
}
