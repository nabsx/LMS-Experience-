from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from datetime import datetime
import json

from .models import (
    User, Category, Course, Section, Lesson, 
    Enrollment, Progress, Review, Wishlist
)

User = get_user_model()


# ==========================================
# MODEL TESTS
# ==========================================

class UserModelTest(TestCase):
    """Test User model dengan role"""
    
    def setUp(self):
        """Setup user untuk testing"""
        self.student_user = User.objects.create_user(
            username='john_student',
            email='john@example.com',
            password='testpass123',
            role='student'
        )
        self.instructor_user = User.objects.create_user(
            username='jane_instructor',
            email='jane@example.com',
            password='testpass123',
            role='instructor'
        )
        self.admin_user = User.objects.create_user(
            username='admin_user',
            email='admin@example.com',
            password='testpass123',
            role='admin'
        )
    
    def test_student_user_creation(self):
        """Test pembuatan student user"""
        self.assertEqual(self.student_user.username, 'john_student')
        self.assertEqual(self.student_user.role, 'student')
        self.assertTrue(self.student_user.check_password('testpass123'))
    
    def test_instructor_user_creation(self):
        """Test pembuatan instructor user"""
        self.assertEqual(self.instructor_user.role, 'instructor')
        self.assertEqual(self.instructor_user.email, 'jane@example.com')
    
    def test_user_role_choices(self):
        """Test role choices valid"""
        valid_roles = ['admin', 'instructor', 'student']
        for user in [self.student_user, self.instructor_user, self.admin_user]:
            self.assertIn(user.role, valid_roles)


class CategoryModelTest(TestCase):
    """Test Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(
            name='Web Development',
            description='Learn web development from basics'
        )
    
    def test_category_creation(self):
        """Test pembuatan category"""
        self.assertEqual(self.category.name, 'Web Development')
        self.assertIsNotNone(self.category.description)
    
    def test_category_str(self):
        """Test string representation"""
        self.assertEqual(str(self.category), 'Web Development')


class CourseModelTest(TestCase):
    """Test Course model dan relasi"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor_user',
            email='instructor@example.com',
            password='testpass123',
            role='instructor'
        )
        self.category = Category.objects.create(
            name='Programming',
            description='Programming courses'
        )
        self.course = Course.objects.create(
            title='Django Fundamentals',
            description='Learn Django from scratch',
            category=self.category,
            instructor=self.instructor
        )
    
    def test_course_creation(self):
        """Test pembuatan course"""
        self.assertEqual(self.course.title, 'Django Fundamentals')
        self.assertEqual(self.course.instructor, self.instructor)
        self.assertEqual(self.course.category, self.category)
    
    def test_course_timestamps(self):
        """Test created_at dan updated_at"""
        self.assertIsNotNone(self.course.created_at)
        self.assertIsNotNone(self.course.updated_at)
    
    def test_course_str(self):
        """Test string representation"""
        self.assertEqual(str(self.course), 'Django Fundamentals')


class SectionModelTest(TestCase):
    """Test Section model"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='inst@example.com',
            password='pass123',
            role='instructor'
        )
        self.course = Course.objects.create(
            title='Python 101',
            description='Basic Python',
            instructor=self.instructor
        )
        self.section = Section.objects.create(
            course=self.course,
            title='Getting Started',
            order=1
        )
    
    def test_section_creation(self):
        """Test pembuatan section"""
        self.assertEqual(self.section.title, 'Getting Started')
        self.assertEqual(self.section.course, self.course)
        self.assertEqual(self.section.order, 1)
    
    def test_section_ordering(self):
        """Test section ordering"""
        section2 = Section.objects.create(
            course=self.course,
            title='Advanced Topics',
            order=2
        )
        sections = Section.objects.filter(course=self.course)
        self.assertEqual(list(sections), [self.section, section2])


class LessonModelTest(TestCase):
    """Test Lesson model"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor',
            email='inst@example.com',
            password='pass123',
            role='instructor'
        )
        self.course = Course.objects.create(
            title='Python 101',
            description='Basic Python',
            instructor=self.instructor
        )
        self.section = Section.objects.create(
            course=self.course,
            title='Basics',
            order=1
        )
        self.lesson = Lesson.objects.create(
            course=self.course,
            section=self.section,
            title='Introduction to Python',
            content='Learn Python basics...',
            order=1
        )
    
    def test_lesson_creation(self):
        """Test pembuatan lesson"""
        self.assertEqual(self.lesson.title, 'Introduction to Python')
        self.assertEqual(self.lesson.course, self.course)
        self.assertEqual(self.lesson.section, self.section)
    
    def test_lesson_content(self):
        """Test lesson content"""
        self.assertIsNotNone(self.lesson.content)
        self.assertTrue(len(self.lesson.content) > 0)


class EnrollmentModelTest(TestCase):
    """Test Enrollment model dan unique_together constraint"""
    
    def setUp(self):
        self.student = User.objects.create_user(
            username='student_user',
            email='student@example.com',
            password='pass123',
            role='student'
        )
        self.instructor = User.objects.create_user(
            username='instructor_user',
            email='instructor@example.com',
            password='pass123',
            role='instructor'
        )
        self.course = Course.objects.create(
            title='Advanced Django',
            description='Advanced Django topics',
            instructor=self.instructor
        )
    
    def test_enrollment_creation(self):
        """Test pembuatan enrollment"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertIsNotNone(enrollment.enrolled_at)
    
    def test_enrollment_unique_constraint(self):
        """Test bahwa student tidak bisa enroll 2x di kursus yang sama"""
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        # Coba enroll lagi di course yang sama
        with self.assertRaises(Exception):
            Enrollment.objects.create(
                student=self.student,
                course=self.course
            )


class ReviewModelTest(TestCase):
    """Test Review model dan validasi rating"""
    
    def setUp(self):
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            role='student'
        )
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='pass123',
            role='instructor'
        )
        self.course = Course.objects.create(
            title='JavaScript 101',
            description='Learn JavaScript',
            instructor=self.instructor
        )
    
    def test_review_creation(self):
        """Test pembuatan review dengan rating valid"""
        review = Review.objects.create(
            course=self.course,
            student=self.student,
            rating=5,
            comment='Excellent course!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Excellent course!')
    
    def test_review_rating_validation(self):
        """Test validasi rating 1-5"""
        # Rating valid
        for rating in range(1, 6):
            review = Review.objects.create(
                course=self.course,
                student=self.student,
                rating=rating
            )
            self.assertEqual(review.rating, rating)
            review.delete()  # Clean up
    
    def test_review_unique_constraint(self):
        """Test bahwa 1 student hanya bisa review 1x per course"""
        Review.objects.create(
            course=self.course,
            student=self.student,
            rating=4
        )
        # Coba review lagi di course yang sama
        with self.assertRaises(Exception):
            Review.objects.create(
                course=self.course,
                student=self.student,
                rating=5
            )


class WishlistModelTest(TestCase):
    """Test Wishlist model"""
    
    def setUp(self):
        self.student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='pass123',
            role='student'
        )
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@example.com',
            password='pass123',
            role='instructor'
        )
        self.course = Course.objects.create(
            title='React Advanced',
            description='Advanced React patterns',
            instructor=self.instructor
        )
    
    def test_wishlist_creation(self):
        """Test pembuatan wishlist item"""
        wishlist = Wishlist.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(wishlist.student, self.student)
        self.assertEqual(wishlist.course, self.course)
    
    def test_wishlist_unique_constraint(self):
        """Test bahwa course tidak bisa ditambah 2x ke wishlist"""
        Wishlist.objects.create(
            student=self.student,
            course=self.course
        )
        # Coba tambah lagi
        with self.assertRaises(Exception):
            Wishlist.objects.create(
                student=self.student,
                course=self.course
            )


# ==========================================
# API ENDPOINT TESTS
# ==========================================

class CourseListAPITest(TestCase):
    """Test endpoint GET /courses/"""
    
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            email='inst@example.com',
            password='pass123',
            role='instructor'
        )
        self.category = Category.objects.create(
            name='Python',
            description='Python courses'
        )
        self.course1 = Course.objects.create(
            title='Python Basics',
            description='Learn Python fundamentals',
            category=self.category,
            instructor=self.instructor
        )
        self.course2 = Course.objects.create(
            title='Advanced Python',
            description='Advanced Python topics',
            category=self.category,
            instructor=self.instructor
        )
    
    def test_list_courses_returns_all(self):
        """Test list courses mengembalikan semua course"""
        response = self.client.get('/api/courses/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 2)
    
    def test_list_courses_response_format(self):
        """Test response format endpoint list courses"""
        response = self.client.get('/api/courses/')
        data = json.loads(response.content)
        self.assertIn('id', data[0])
        self.assertIn('title', data[0])
        self.assertIn('description', data[0])


class UserRegistrationAPITest(TestCase):
    """Test endpoint POST /register/"""
    
    def setUp(self):
        self.client = Client()
    
    def test_register_new_user(self):
        """Test registrasi user baru"""
        payload = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'student'
        }
        response = self.client.post('/api/register/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_register_duplicate_username(self):
        """Test registrasi dengan username yang sudah ada"""
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='pass123'
        )
        payload = {
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'password': 'pass123',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'student'
        }
        response = self.client.post('/api/register/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
    
    def test_register_duplicate_email(self):
        """Test registrasi dengan email yang sudah ada"""
        User.objects.create_user(
            username='user1',
            email='same@example.com',
            password='pass123'
        )
        payload = {
            'username': 'user2',
            'email': 'same@example.com',
            'password': 'pass123',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'student'
        }
        response = self.client.post('/api/register/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)
