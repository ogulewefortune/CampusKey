// Import Flutter's Material Design library - provides UI components
import 'package:flutter/material.dart';
// Import LoginScreen from main.dart - needed for navigation after splash
import '../main.dart';

// SplashScreen class - Initial loading screen shown when app starts
// StatefulWidget allows this widget to perform actions (like navigation) after a delay
class SplashScreen extends StatefulWidget {
  // Override createState - creates the state object that manages this widget
  @override
  _SplashScreenState createState() => _SplashScreenState();
}

// _SplashScreenState class - Manages the state and behavior of SplashScreen
// The underscore prefix makes it private to this file
class _SplashScreenState extends State<SplashScreen> {
  // initState method - called once when the widget is first created
  // This is where we set up the timer to navigate after 5 seconds
  @override
  void initState() {
    super.initState(); // Call parent's initState (required)
    // Navigate to login screen after 5 seconds
    // Future.delayed waits for specified duration, then executes callback
    Future.delayed(Duration(seconds: 5), () {
      // Navigator.pushReplacement replaces current screen with new one
      // Unlike push(), this removes splash screen from navigation stack (can't go back)
      Navigator.pushReplacement(
        context, // Current widget's context (required for navigation)
        MaterialPageRoute(builder: (context) => LoginScreen()), // Navigate to LoginScreen
      );
    });
  }

  // Override build method - defines the UI structure of SplashScreen
  @override
  Widget build(BuildContext context) {
    // Scaffold provides basic app structure
    return Scaffold(
      backgroundColor: Colors.blue, // Blue background color for splash screen
      // Body - main content area
      body: Center(
        // Center widget centers its child both horizontally and vertically
        // Column widget arranges children vertically
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center, // Center content vertically
          children: [
            // App Logo - You can replace this with your actual logo image
            // Icon widget displays a Material Design icon
            Icon(
              Icons.key, // Key icon (represents CampusKey branding)
              size: 120, // Icon size in pixels
              color: Colors.white, // White color for icon
            ),
            SizedBox(height: 20), // Empty space 20 pixels tall (spacing between logo and text)
            // App name text
            Text(
              'CampusKey', // App name displayed on splash screen
              style: TextStyle(
                fontSize: 36, // Text size - 36 pixels
                fontWeight: FontWeight.bold, // Make text bold
                color: Colors.white, // White text color
              ),
            ),
            SizedBox(height: 40), // Empty space 40 pixels tall (spacing between text and spinner)
            // Loading indicator - shows app is loading/initializing
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white), // White spinner color
            ),
          ],
        ),
      ),
    );
  }
}
