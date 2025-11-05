// Verification Code Widget - Reusable widget for displaying verification codes
import 'package:flutter/material.dart';

class VerificationCodeWidget extends StatelessWidget {
  final String code;
  final int expirySeconds;
  final VoidCallback onRefresh;

  const VerificationCodeWidget({
    Key? key,
    required this.code,
    required this.expirySeconds,
    required this.onRefresh,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    String minutes = (expirySeconds ~/ 60).toString().padLeft(2, '0');
    String seconds = (expirySeconds % 60).toString().padLeft(2, '0');

    return Container(
      padding: EdgeInsets.all(20),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.blue),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Text(
            code,
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, letterSpacing: 2),
          ),
          SizedBox(height: 10),
          Text(
            'Expires in: $minutes:$seconds',
            style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 10),
          ElevatedButton.icon(
            onPressed: onRefresh,
            icon: Icon(Icons.refresh),
            label: Text('Generate New Code'),
          ),
        ],
      ),
    );
  }
}

