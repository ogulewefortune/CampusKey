// Access Card Widget - Reusable card for displaying access information
import 'package:flutter/material.dart';

class AccessCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color? color;

  const AccessCard({
    Key? key,
    required this.title,
    required this.subtitle,
    required this.icon,
    this.color,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.only(bottom: 10),
      child: ListTile(
        leading: Icon(icon, color: color ?? Colors.blue),
        title: Text(title),
        subtitle: Text(subtitle),
        trailing: Icon(Icons.verified, color: Colors.green),
      ),
    );
  }
}

