from types import SimpleNamespace

from django.test import SimpleTestCase

from fairhire.apps.matching.engine import score_candidate


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
