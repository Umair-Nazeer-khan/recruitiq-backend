from types import SimpleNamespace

from django.test import SimpleTestCase

from fairhire.apps.matching.engine import score_candidate
from fairhire.apps.resume.parser import parse_resume_rule_based


class ScoreCandidateTests(SimpleTestCase):
    def test_invalid_weights_are_clamped_and_normalized(self):
        candidate = SimpleNamespace(
            id=1,
            name='Ali Khan',
            original_name='Ali Khan',
            email='ali@example.com',
            phone='+923001234567',
            location='Lahore',
            skills=['Python', 'Django'],
            experience_years=3,
            education_level='MSc',
            raw_text='Python Django developer with 3 years experience.',
            status='pending',
        )

        job = {
            'required_skills': ['Python', 'Django'],
            'optional_skills': ['REST API'],
            'min_experience': 2,
            'education_level': 'MSc',
            'skill_weight': -10,
            'experience_weight': 5,
            'education_weight': 6,
        }

        result = score_candidate(candidate, job)

        self.assertGreaterEqual(result['final_score'], 0)
        self.assertLessEqual(result['final_score'], 100)

    def test_equivalent_skill_variants_match(self):
        candidate = SimpleNamespace(
            id=2,
            name='Sara Ali',
            original_name='Sara Ali',
            email='sara@example.com',
            phone='+923009876543',
            location='Karachi',
            skills=['REST APIs', 'Django'],
            experience_years=2,
            education_level='BSCS',
            raw_text='Backend developer with REST APIs and Django experience.',
            status='pending',
        )

        job = {
            'required_skills': ['rest api', 'django'],
            'optional_skills': [],
            'min_experience': 2,
            'education_level': 'BSc / BE',
            'skill_weight': 0.5,
            'experience_weight': 0.3,
            'education_weight': 0.2,
        }

        result = score_candidate(candidate, job)

        self.assertIn('rest api', result['matched_skills'])
        self.assertGreaterEqual(result['final_score'], 0)
        self.assertLessEqual(result['final_score'], 100)

    def test_real_cv_structure_is_parsed_more_cleanly(self):
        text = '''
MUHAMMAD ALI
Email: ali@gmail.com | Phone: +92 300 1234567
Lahore, Pakistan

PROFESSIONAL SUMMARY
Python and Django developer with 3 years experience in web applications.

SKILLS
Python, Django, REST API, React, SQL, Docker, Git

EDUCATION
BSCS, University of Lahore, 2018 - 2022

EXPERIENCE
Software Engineer
ABC Tech | Lahore | 2022 - Present
- Built APIs with Django and REST framework
- Worked with React JS and SQL databases
'''

        parsed = parse_resume_rule_based(text)

        self.assertEqual(parsed['name'], 'MUHAMMAD ALI')
        self.assertIn('python', [s.lower() for s in parsed['skills']])
        self.assertIn('django', [s.lower() for s in parsed['skills']])
        self.assertIn('bsc', parsed['education_level'].lower())
        self.assertEqual(parsed['experience_years'], 3.0)
        self.assertEqual(parsed['work_history'][0]['company'], 'ABC Tech')
        self.assertEqual(parsed['work_history'][0]['role'], 'Software Engineer')
