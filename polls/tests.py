import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_hidden_future(self):
        question = create_question(question_text='Future question', days=30)
        assert question.is_hidden()

    def test_is_hidden_no_choices(self):
        question = create_question(question_text='Future question', days=-30, choices=False)
        assert question.is_hidden()


def create_question(question_text, days, choices=True) -> Question:
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    if choices:
        Choice.objects.create(question=question, choice_text='Choice 1')
        Choice.objects.create(question=question, choice_text='Choice 2')
    return question


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question>'])

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        create_question(question_text="Past question", days=-30)
        create_question(question_text="Future question", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question>'])

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question(question_text="Past question 1", days=-30)
        create_question(question_text="Past question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'], ['<Question: Past question 2>', '<Question: Past question 1>']
        )


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:detail', args=[future_question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past question', days=-5)
        url = reverse('polls:detail', args=[past_question.id])
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_past_question_no_choices(self):
        question = create_question(question_text='Past Question', days=-5, choices=False)
        url = reverse('polls:detail', args=[question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_admin(self):
        password = 'password'
        admin = User.objects.create_superuser('admin', '', password)
        self.client.login(username=admin.username, password=password)

        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:detail', args=[future_question.id])
        response = self.client.get(url)
        self.assertContains(response, future_question.question_text)


class QuestionResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:results', args=[future_question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question', days=-5)
        url = reverse('polls:results', args=[past_question.id])
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_past_question_no_choices(self):
        question = create_question(question_text='Past Question', days=-5, choices=False)
        url = reverse('polls:results', args=[question.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_future_question_admin(self):
        password = 'password'
        admin = User.objects.create_superuser('admin', '', password)
        self.client.login(username=admin.username, password=password)

        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:detail', args=[future_question.id])
        response = self.client.get(url)
        self.assertContains(response, future_question.question_text)


class VoteViewTests(TestCase):
    def test_question_vote(self):
        past_question = create_question(question_text='Past question', days=-5)
        first_choice = past_question.choice_set.first()
        self.assertEqual(first_choice.votes, 0)

        url = reverse('polls:vote', args=[past_question.id])
        response = self.client.post(url, data={'choice': first_choice.id}, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:results', args=[past_question.id]))
        first_choice.refresh_from_db()
        self.assertEqual(first_choice.votes, 1)

    def test_question_vote_no_choice(self):
        past_question = create_question(question_text='Past question', days=-5)
        first_choice = past_question.choice_set.first()
        self.assertEqual(first_choice.votes, 0)

        url = reverse('polls:vote', args=[past_question.id])
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        first_choice.refresh_from_db()
        self.assertEqual(first_choice.votes, 0)
