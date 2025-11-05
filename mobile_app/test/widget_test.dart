// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter_test/flutter_test.dart';

import 'package:campuskey/main.dart';

void main() {
  testWidgets('CampusKey login screen displays correctly', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(MyApp());

    // Verify that the login screen displays
    expect(find.text('CampusKey Login'), findsOneWidget);
    expect(find.text('Username'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
    expect(find.text('LOGIN'), findsOneWidget);
    
    // Verify role buttons are present
    expect(find.text('Student'), findsOneWidget);
    expect(find.text('Professor'), findsOneWidget);
    expect(find.text('Admin'), findsOneWidget);
  });
}
