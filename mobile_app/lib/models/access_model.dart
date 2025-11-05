// Access Model - Data model for access permissions
class AccessModel {
  final String buildingName;
  final String accessLevel;
  final String timeRestriction;
  final List<String> fileAccess;

  AccessModel({
    required this.buildingName,
    required this.accessLevel,
    required this.timeRestriction,
    required this.fileAccess,
  });
}

