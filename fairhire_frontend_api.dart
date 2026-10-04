// FairHire Flutter API contract template
// Copy this file into your Flutter project and adjust imports and package names as needed.

import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

class ApiConfig {
  static const String baseUrl = 'https://proud-wholeness-production-2929.up.railway.app/api/v1';
  // static const String baseUrl = 'http://localhost:8000/api/v1';
  static const String authPath = '/auth';
  static const String resumesPath = '/resumes';
  static const String jobsPath = '/jobs';
  static const String matchingPath = '/matching';
}

class UserModel {
  final int id;
  final String name;
  final String email;
  final String role;
  final DateTime? createdAt;

  UserModel({
    required this.id,
    required this.name,
    required this.email,
    required this.role,
    this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      role: json['role'] ?? 'hr_manager',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'])
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'email': email,
        'role': role,
        'created_at': createdAt?.toIso8601String(),
      };
}

class AuthResponse {
  final UserModel user;
  final String access;
  final String refresh;
  final String message;

  AuthResponse({
    required this.user,
    required this.access,
    required this.refresh,
    required this.message,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      user: UserModel.fromJson(json['user'] ?? {}),
      access: json['access'] ?? '',
      refresh: json['refresh'] ?? '',
      message: json['message'] ?? '',
    );
  }
}

class CandidateModel {
  final int id;
  final String name;
  final String email;
  final String phone;
  final String location;
  final String education;
  final String educationLevel;
  final double experienceYears;
  final List<String> skills;
  final List<String> languages;
  final List<Map<String, dynamic>> projects;
  final List<String> certifications;
  final List<String> awards;
  final List<Map<String, dynamic>> workHistory;
  final double? matchScore;
  final double? skillScore;
  final double? experienceScore;
  final double? educationScore;
  final List<String> missingSkills;
  final String scoreExplanation;
  final String status;
  final String hrNotes;
  final String originalName;
  final DateTime? createdAt;
  final String? resumeFileUrl;

  CandidateModel({
    required this.id,
    required this.name,
    required this.email,
    required this.phone,
    required this.location,
    required this.education,
    required this.educationLevel,
    required this.experienceYears,
    required this.skills,
    required this.languages,
    required this.projects,
    required this.certifications,
    required this.awards,
    required this.workHistory,
    this.matchScore,
    this.skillScore,
    this.experienceScore,
    this.educationScore,
    required this.missingSkills,
    required this.scoreExplanation,
    required this.status,
    required this.hrNotes,
    required this.originalName,
    this.createdAt,
    this.resumeFileUrl,
  });

  factory CandidateModel.fromJson(Map<String, dynamic> json) {
    return CandidateModel(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      phone: json['phone'] ?? '',
      location: json['location'] ?? '',
      education: json['education'] ?? '',
      educationLevel: json['education_level'] ?? '',
      experienceYears: (json['experience_years'] ?? 0).toDouble(),
      skills: List<String>.from(json['skills'] ?? []),
      languages: List<String>.from(json['languages'] ?? []),
      projects: List<Map<String, dynamic>>.from(json['projects'] ?? []),
      certifications: List<String>.from(json['certifications'] ?? []),
      awards: List<String>.from(json['awards'] ?? []),
      workHistory: List<Map<String, dynamic>>.from(json['work_history'] ?? []),
      matchScore: json['match_score'] != null
          ? (json['match_score'] as num).toDouble()
          : null,
      skillScore: json['skill_score'] != null
          ? (json['skill_score'] as num).toDouble()
          : null,
      experienceScore: json['experience_score'] != null
          ? (json['experience_score'] as num).toDouble()
          : null,
      educationScore: json['education_score'] != null
          ? (json['education_score'] as num).toDouble()
          : null,
      missingSkills: List<String>.from(json['missing_skills'] ?? []),
      scoreExplanation: json['score_explanation'] ?? '',
      status: json['status'] ?? 'pending',
      hrNotes: json['hr_notes'] ?? '',
      originalName: json['original_name'] ?? '',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'])
          : null,
      resumeFileUrl: json['resume_file_url'],
    );
  }
}

class CandidateListItem {
  final int id;
  final String name;
  final String email;
  final double experienceYears;
  final String educationLevel;
  final List<String> skills;
  final double? matchScore;
  final String status;
  final DateTime? createdAt;

  CandidateListItem({
    required this.id,
    required this.name,
    required this.email,
    required this.experienceYears,
    required this.educationLevel,
    required this.skills,
    this.matchScore,
    required this.status,
    this.createdAt,
  });

  factory CandidateListItem.fromJson(Map<String, dynamic> json) {
    return CandidateListItem(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      experienceYears: (json['experience_years'] ?? 0).toDouble(),
      educationLevel: json['education_level'] ?? '',
      skills: List<String>.from(json['skills'] ?? []),
      matchScore: json['match_score'] != null
          ? (json['match_score'] as num).toDouble()
          : null,
      status: json['status'] ?? 'pending',
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'])
          : null,
    );
  }
}

class DashboardStats {
  final int totalCvs;
  final int shortlisted;
  final int accepted;
  final int rejected;
  final int pending;
  final int onHold;

  DashboardStats({
    required this.totalCvs,
    required this.shortlisted,
    required this.accepted,
    required this.rejected,
    required this.pending,
    required this.onHold,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      totalCvs: json['total_cvs'] ?? 0,
      shortlisted: json['shortlisted'] ?? 0,
      accepted: json['accepted'] ?? 0,
      rejected: json['rejected'] ?? 0,
      pending: json['pending'] ?? 0,
      onHold: json['on_hold'] ?? 0,
    );
  }
}

class JobModel {
  final int id;
  final String title;
  final String department;
  final String location;
  final String jobType;
  final List<String> requiredSkills;
  final List<String> optionalSkills;
  final int minExperience;
  final String educationLevel;
  final int? salaryMin;
  final int? salaryMax;
  final double skillWeight;
  final double experienceWeight;
  final double educationWeight;
  final bool isActive;
  final DateTime? createdAt;

  JobModel({
    required this.id,
    required this.title,
    required this.department,
    required this.location,
    required this.jobType,
    required this.requiredSkills,
    required this.optionalSkills,
    required this.minExperience,
    required this.educationLevel,
    this.salaryMin,
    this.salaryMax,
    required this.skillWeight,
    required this.experienceWeight,
    required this.educationWeight,
    required this.isActive,
    this.createdAt,
  });

  factory JobModel.fromJson(Map<String, dynamic> json) {
    return JobModel(
      id: json['id'] ?? 0,
      title: json['title'] ?? '',
      department: json['department'] ?? '',
      location: json['location'] ?? '',
      jobType: json['job_type'] ?? 'full_time',
      requiredSkills: List<String>.from(json['required_skills'] ?? []),
      optionalSkills: List<String>.from(json['optional_skills'] ?? []),
      minExperience: json['min_experience'] ?? 0,
      educationLevel: json['education_level'] ?? '',
      salaryMin: json['salary_min'],
      salaryMax: json['salary_max'],
      skillWeight: (json['skill_weight'] ?? 0.5).toDouble(),
      experienceWeight: (json['experience_weight'] ?? 0.3).toDouble(),
      educationWeight: (json['education_weight'] ?? 0.2).toDouble(),
      isActive: json['is_active'] ?? true,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'])
          : null,
    );
  }
}

class MatchResultModel {
  final int candidateId;
  final String candidateName;
  final String email;
  final double experienceYears;
  final String educationLevel;
  final List<String> skills;
  final double finalScore;
  final double skillScore;
  final double experienceScore;
  final double educationScore;
  final List<String> missingSkills;
  final String explanation;
  final String status;

  MatchResultModel({
    required this.candidateId,
    required this.candidateName,
    required this.email,
    required this.experienceYears,
    required this.educationLevel,
    required this.skills,
    required this.finalScore,
    required this.skillScore,
    required this.experienceScore,
    required this.educationScore,
    required this.missingSkills,
    required this.explanation,
    required this.status,
  });

  factory MatchResultModel.fromJson(Map<String, dynamic> json) {
    return MatchResultModel(
      candidateId: json['candidate_id'] ?? 0,
      candidateName: json['candidate_name'] ?? '',
      email: json['email'] ?? '',
      experienceYears: (json['experience_years'] ?? 0).toDouble(),
      educationLevel: json['education_level'] ?? '',
      skills: List<String>.from(json['skills'] ?? []),
      finalScore: (json['final_score'] ?? 0).toDouble(),
      skillScore: (json['skill_score'] ?? 0).toDouble(),
      experienceScore: (json['experience_score'] ?? 0).toDouble(),
      educationScore: (json['education_score'] ?? 0).toDouble(),
      missingSkills: List<String>.from(json['missing_skills'] ?? []),
      explanation: json['explanation'] ?? '',
      status: json['status'] ?? 'pending',
    );
  }
}

class MatchResponse {
  final String message;
  final MatchStats stats;
  final List<MatchResultModel> results;

  MatchResponse({
    required this.message,
    required this.stats,
    required this.results,
  });

  factory MatchResponse.fromJson(Map<String, dynamic> json) {
    return MatchResponse(
      message: json['message'] ?? '',
      stats: MatchStats.fromJson(json['stats'] ?? {}),
      results: (json['results'] as List? ?? [])
          .map((e) => MatchResultModel.fromJson(e))
          .toList(),
    );
  }
}

class MatchStats {
  final int total;
  final int goodMatch;
  final int partial;
  final int noMatch;

  MatchStats({
    required this.total,
    required this.goodMatch,
    required this.partial,
    required this.noMatch,
  });

  factory MatchStats.fromJson(Map<String, dynamic> json) {
    return MatchStats(
      total: json['total'] ?? 0,
      goodMatch: json['good_match'] ?? 0,
      partial: json['partial'] ?? 0,
      noMatch: json['no_match'] ?? 0,
    );
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  @override
  String toString() => 'ApiException(statusCode: $statusCode, message: $message)';
}

class FairHireApiService {
  final String baseUrl;
  final String? token;

  FairHireApiService({
    this.baseUrl = ApiConfig.baseUrl,
    this.token,
  });

  Map<String, String> getHeaders({bool isJson = true, bool includeAuth = true}) {
    final headers = <String, String>{};
    if (isJson) {
      headers['Content-Type'] = 'application/json';
    }
    if (includeAuth && token != null && token!.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  Future<AuthResponse> register({
    required String name,
    required String email,
    required String password,
  }) async {
    final uri = Uri.parse('$baseUrl/auth/register/');
    final body = jsonEncode({
      'name': name,
      'email': email,
      'password': password,
    });

    final response = await http.post(uri, headers: getHeaders(), body: body);
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 201) {
      return AuthResponse.fromJson(decoded);
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<AuthResponse> login({
    required String email,
    required String password,
    String? fcmToken,
  }) async {
    final uri = Uri.parse('$baseUrl/auth/login/');
    final data = {
      'email': email,
      'password': password,
      if (fcmToken != null && fcmToken.isNotEmpty) 'fcm_token': fcmToken,
    };

    final response = await http.post(
      uri,
      headers: getHeaders(),
      body: jsonEncode(data),
    );
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return AuthResponse.fromJson(decoded);
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<void> logout({required String refreshToken}) async {
    final uri = Uri.parse('$baseUrl/auth/logout/');
    final response = await http.post(
      uri,
      headers: getHeaders(),
      body: jsonEncode({'refresh': refreshToken}),
    );

    if (response.statusCode != 200) {
      throw ApiException(response.statusCode, response.body);
    }
  }

  Future<UserModel> getProfile() async {
    final uri = Uri.parse('$baseUrl/auth/profile/');
    final response = await http.get(uri, headers: getHeaders());
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return UserModel.fromJson(decoded);
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<void> updateFcmToken({required String fcmToken}) async {
    final uri = Uri.parse('$baseUrl/auth/update-fcm/');
    final response = await http.patch(
      uri,
      headers: getHeaders(),
      body: jsonEncode({'fcm_token': fcmToken}),
    );

    if (response.statusCode != 200) {
      throw ApiException(response.statusCode, response.body);
    }
  }

  Future<String> refreshAccessToken({required String refreshToken}) async {
    final uri = Uri.parse('$baseUrl/auth/token/refresh/');
    final response = await http.post(
      uri,
      headers: getHeaders(),
      body: jsonEncode({'refresh': refreshToken}),
    );
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return decoded['access'] ?? '';
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<List<CandidateListItem>> listCandidates({String? status}) async {
    final query = status == null ? '' : '?status=$status';
    final uri = Uri.parse('$baseUrl/resumes/$query');
    final response = await http.get(uri, headers: getHeaders());
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      final list = decoded['candidates'] as List? ?? [];
      return list.map((e) => CandidateListItem.fromJson(e)).toList();
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<CandidateModel> uploadResume({required File file}) async {
    final uri = Uri.parse('$baseUrl/resumes/upload/');
    final request = http.MultipartRequest('POST', uri);

    if (token != null && token!.isNotEmpty) {
      request.headers['Authorization'] = 'Bearer $token';
    }
    request.files.add(await http.MultipartFile.fromPath('file', file.path));

    final streamedResponse = await request.send();
    final responseBody = await streamedResponse.stream.bytesToString();
    final decoded = jsonDecode(responseBody);

    if (streamedResponse.statusCode == 201) {
      return CandidateModel.fromJson(decoded['candidate'] ?? {});
    }
    throw ApiException(streamedResponse.statusCode, decoded.toString());
  }

  Future<CandidateModel> getCandidateDetail(int candidateId) async {
    final uri = Uri.parse('$baseUrl/resumes/$candidateId/');
    final response = await http.get(uri, headers: getHeaders());
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return CandidateModel.fromJson(decoded);
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<void> updateCandidateStatus({
    required int candidateId,
    required String status,
    String? hrNotes,
  }) async {
    final uri = Uri.parse('$baseUrl/resumes/$candidateId/status/');
    final response = await http.patch(
      uri,
      headers: getHeaders(),
      body: jsonEncode({
        'status': status,
        if (hrNotes != null) 'hr_notes': hrNotes,
      }),
    );
    final decoded = jsonDecode(response.body);

    if (response.statusCode != 200) {
      throw ApiException(response.statusCode, decoded.toString());
    }
  }

  Future<DashboardStats> getResumeStats() async {
    final uri = Uri.parse('$baseUrl/resumes/stats/');
    final response = await http.get(uri, headers: getHeaders());
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return DashboardStats.fromJson(decoded);
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<http.StreamedResponse> downloadResume(int candidateId) async {
    final uri = Uri.parse('$baseUrl/resumes/$candidateId/download/');
    final request = http.Request('GET', uri);
    request.headers['Authorization'] = 'Bearer $token';
    return request.send();
  }

  Future<List<JobModel>> listJobs() async {
    final uri = Uri.parse('$baseUrl/jobs/');
    final response = await http.get(uri, headers: getHeaders());
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      final list = decoded as List? ?? [];
      return list.map((e) => JobModel.fromJson(e)).toList();
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<JobModel> createJob({required Map<String, dynamic> jobData}) async {
    final uri = Uri.parse('$baseUrl/jobs/');
    final response = await http.post(
      uri,
      headers: getHeaders(),
      body: jsonEncode(jobData),
    );
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 201) {
      return JobModel.fromJson(decoded);
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<JobModel> getJob(int jobId) async {
    final uri = Uri.parse('$baseUrl/jobs/$jobId/');
    final response = await http.get(uri, headers: getHeaders());
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return JobModel.fromJson(decoded);
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<JobModel> updateJob({
    required int jobId,
    required Map<String, dynamic> jobData,
  }) async {
    final uri = Uri.parse('$baseUrl/jobs/$jobId/');
    final response = await http.put(
      uri,
      headers: getHeaders(),
      body: jsonEncode(jobData),
    );
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return JobModel.fromJson(decoded);
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<void> deleteJob(int jobId) async {
    final uri = Uri.parse('$baseUrl/jobs/$jobId/');
    final response = await http.delete(uri, headers: getHeaders());

    if (response.statusCode != 204) {
      throw ApiException(response.statusCode, response.body);
    }
  }

  Future<MatchResponse> matchCandidates({
    int? jobId,
    Map<String, dynamic>? inlineJob,
  }) async {
    final uri = Uri.parse('$baseUrl/matching/');
    final payload = <String, dynamic>{};

    if (jobId != null) {
      payload['job_id'] = jobId;
    }

    if (inlineJob != null) {
      payload.addAll(inlineJob);
    }

    final response = await http.post(
      uri,
      headers: getHeaders(),
      body: jsonEncode(payload),
    );
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return MatchResponse.fromJson(decoded);
    }
    throw ApiException(response.statusCode, decoded.toString());
  }

  Future<List<MatchResultModel>> getMatchResults({double? minScore}) async {
    final query = minScore == null ? '' : '?min_score=$minScore';
    final uri = Uri.parse('$baseUrl/matching/results/$query');
    final response = await http.get(uri, headers: getHeaders());
    final decoded = jsonDecode(response.body);

    if (response.statusCode == 200) {
      final list = decoded['results'] as List? ?? [];
      return list.map((e) => MatchResultModel.fromJson(e)).toList();
    }
    throw ApiException(response.statusCode, decoded.toString());
  }
}

// Example usage
Future<void> exampleUsage() async {
  final api = FairHireApiService(token: 'YOUR_ACCESS_TOKEN');

  // Login
  // final auth = await api.login(email: 'user@example.com', password: 'secret123');
  // print(auth.access);

  // Get dashboard stats
  // final stats = await api.getResumeStats();
  // print(stats.totalCvs);

  // List candidates
  // final candidates = await api.listCandidates(status: 'shortlisted');
  // print(candidates.first.name);

  // Create a job
  // final job = await api.createJob(jobData: {
  //   'title': 'Flutter Developer',
  //   'department': 'Mobile',
  //   'location': 'Lahore',
  //   'job_type': 'full_time',
  //   'required_skills': ['Flutter', 'Dart'],
  //   'optional_skills': ['Firebase'],
  //   'min_experience': 2,
  //   'education_level': 'BSc / BE',
  //   'salary_min': 80000,
  //   'salary_max': 120000,
  //   'skill_weight': 0.5,
  //   'experience_weight': 0.3,
  //   'education_weight': 0.2,
  // });

  // Match candidates
  // final match = await api.matchCandidates(
  //   inlineJob: {
  //     'title': 'Flutter Dev',
  //     'required_skills': ['Flutter', 'Dart'],
  //     'optional_skills': ['Python'],
  //     'min_experience': 2,
  //     'education_level': 'BSc / BE',
  //     'skill_weight': 0.5,
  //     'experience_weight': 0.3,
  //     'education_weight': 0.2,
  //   },
  // );
}
