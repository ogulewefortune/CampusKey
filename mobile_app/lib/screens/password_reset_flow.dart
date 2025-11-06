// Password Reset Flow Screen - Multi-step password recovery process
import 'package:flutter/material.dart';
import '../main.dart';

class PasswordResetFlowScreen extends StatefulWidget {
  const PasswordResetFlowScreen({super.key});

  @override
  _PasswordResetFlowScreenState createState() => _PasswordResetFlowScreenState();
}

class _PasswordResetFlowScreenState extends State<PasswordResetFlowScreen> {
  int _currentStep = 0;
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _codeController = TextEditingController();
  final TextEditingController _newPasswordController = TextEditingController();
  final TextEditingController _confirmPasswordController = TextEditingController();
  String _verificationCode = '';

  List<Step> get _steps => [
    Step(
      title: Text('Enter Email'),
      content: Column(
        children: [
          TextField(
            controller: _emailController,
            decoration: InputDecoration(
              labelText: 'Email Address',
              prefixIcon: Icon(Icons.email),
              border: OutlineInputBorder(),
            ),
            keyboardType: TextInputType.emailAddress,
          ),
          SizedBox(height: 20),
          ElevatedButton(
            onPressed: _sendVerificationCode,
            style: ElevatedButton.styleFrom(
              minimumSize: Size(double.infinity, 50),
            ),
            child: Text('Send Verification Code'),
          ),
        ],
      ),
      isActive: _currentStep >= 0,
    ),
    Step(
      title: Text('Enter Code'),
      content: Column(
        children: [
          Text('Verification code sent to ${_emailController.text}'),
          SizedBox(height: 20),
          TextField(
            controller: _codeController,
            decoration: InputDecoration(
              labelText: 'Verification Code',
              prefixIcon: Icon(Icons.lock),
              border: OutlineInputBorder(),
            ),
            keyboardType: TextInputType.number,
          ),
        ],
      ),
      isActive: _currentStep >= 1,
    ),
    Step(
      title: Text('New Password'),
      content: Column(
        children: [
          TextField(
            controller: _newPasswordController,
            decoration: InputDecoration(
              labelText: 'New Password',
              prefixIcon: Icon(Icons.lock_outline),
              border: OutlineInputBorder(),
            ),
            obscureText: true,
          ),
          SizedBox(height: 15),
          TextField(
            controller: _confirmPasswordController,
            decoration: InputDecoration(
              labelText: 'Confirm Password',
              prefixIcon: Icon(Icons.lock),
              border: OutlineInputBorder(),
            ),
            obscureText: true,
          ),
        ],
      ),
      isActive: _currentStep >= 2,
    ),
    Step(
      title: Text('Success'),
      content: Column(
        children: [
          Icon(Icons.check_circle, size: 80, color: Colors.green),
          SizedBox(height: 20),
          Text(
            'Password Reset Successful!',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 10),
          Text('You can now login with your new password.'),
        ],
      ),
      isActive: _currentStep >= 3,
    ),
  ];

  void _sendVerificationCode() {
    if (_emailController.text.isNotEmpty) {
      setState(() {
        _verificationCode = '123456'; // Mock code
        _currentStep = 1;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Verification code sent to ${_emailController.text}')),
      );
    }
  }

  void _verifyCode() {
    if (_codeController.text == _verificationCode) {
      setState(() {
        _currentStep = 2;
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Invalid verification code')),
      );
    }
  }

  void _resetPassword() {
    if (_newPasswordController.text == _confirmPasswordController.text &&
        _newPasswordController.text.length >= 6) {
      setState(() {
        _currentStep = 3;
      });
      Future.delayed(Duration(seconds: 2), () {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (context) => LoginScreen()),
        );
      });
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Passwords do not match or too short')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Reset Password'),
        backgroundColor: Colors.blue[900],
      ),
      body: Stepper(
        currentStep: _currentStep,
        steps: _steps,
        onStepContinue: () {
          if (_currentStep == 1) {
            _verifyCode();
          } else if (_currentStep == 2) {
            _resetPassword();
          } else if (_currentStep < _steps.length - 1) {
            setState(() {
              _currentStep++;
            });
          }
        },
        onStepCancel: () {
          if (_currentStep > 0) {
            setState(() {
              _currentStep--;
            });
          } else {
            Navigator.pop(context);
          }
        },
      ),
    );
  }
}

