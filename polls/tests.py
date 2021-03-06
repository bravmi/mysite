import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Choice, Question, Comment, Profile


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        assert future_question.was_published_recently() is False

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        assert old_question.was_published_recently() is False

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        assert recent_question.was_published_recently() is True

    def test_is_hidden_future(self):
        question = create_question(question_text='Future question', days=30)
        assert question.is_hidden()

    def test_is_hidden_no_choices(self):
        question = create_question(question_text='Future question', days=-30, nchoices=0)
        assert question.is_hidden()


class ProfileModelTests(TestCase):
    def test_auto_profile_creation(self):
        password = 'password'
        user = User.objects.create_user(username='username', password=password)
        assert len(Profile.objects.all()) == 1
        assert user.profile.user is user


class ChoiceModelTests(TestCase):
    def test_choices_order(self):
        question = create_question(question_text='Past Question', days=-5, nchoices=2)
        first, second = question.choice_set.all()
        first.votes = 1
        first.save()
        second.votes = 2
        second.save()
        assert question.choice_set.first() == question.choice_set.order_by('-votes').first()


def create_question(question_text, days, nchoices=2) -> Question:
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    question = Question.objects.create(question_text=question_text, pub_date=time)
    if nchoices:
        for i in range(nchoices):
            Choice.objects.create(question=question, choice_text=f'Choice {i + 1}')
    return question


class IndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        assert response.status_code == 200
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


class QuestionViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:question', args=[future_question.pk])
        response = self.client.get(url)
        assert response.status_code == 404

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past question', days=-5)
        url = reverse('polls:question', args=[past_question.pk])
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_past_question_no_choices(self):
        question = create_question(question_text='Past Question', days=-5, nchoices=0)
        url = reverse('polls:question', args=[question.pk])
        response = self.client.get(url)
        assert response.status_code == 404

    def test_future_question_admin(self):
        password = 'password'
        admin = User.objects.create_superuser(username='admin', password=password)
        self.client.login(username=admin.username, password=password)

        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:question', args=[future_question.pk])
        response = self.client.get(url)
        self.assertContains(response, future_question.question_text)


class ResultsViewTests(TestCase):
    def test_future_question(self):
        """
        The results view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:results', args=[future_question.pk])
        response = self.client.get(url)
        assert response.status_code == 404

    def test_past_question(self):
        """
        The results view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question', days=-5)
        url = reverse('polls:results', args=[past_question.pk])
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_past_question_no_choices(self):
        question = create_question(question_text='Past Question', days=-5, nchoices=0)
        url = reverse('polls:results', args=[question.pk])
        response = self.client.get(url)
        assert response.status_code == 404

    def test_future_question_admin(self):
        password = 'password'
        admin = User.objects.create_superuser(username='admin', password=password)
        self.client.login(username=admin.username, password=password)

        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:results', args=[future_question.pk])
        response = self.client.get(url)
        self.assertContains(response, future_question.question_text)
        self.assertContains(response, future_question.choice_set.first().choice_text)


class VoteViewTests(TestCase):
    def test_question_vote(self):
        password = "/'].;[,lp"
        user = User.objects.create_user(username='user', password=password)
        self.client.login(username=user.username, password=password)

        past_question = create_question(question_text='Past question', days=-5)
        first_choice = past_question.choice_set.first()
        assert first_choice.votes == 0

        url = reverse('polls:vote', args=[past_question.pk])
        response = self.client.post(url, data={'choice': first_choice.pk}, follow=True)
        self.assertRedirects(response, reverse('polls:results', args=[past_question.pk]))
        first_choice.refresh_from_db()
        assert first_choice.votes == 1

    def test_vote_login_redirect(self):
        past_question = create_question(question_text='Past question', days=-5)
        first_choice = past_question.choice_set.first()
        assert first_choice.votes == 0

        url = reverse('polls:vote', args=[past_question.pk])
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, f'{reverse("login")}?next={url}')

    def test_vote_no_choice(self):
        password = "/'].;[,lp"
        user = User.objects.create_user(username='user', password=password)
        self.client.login(username=user.username, password=password)

        past_question = create_question(question_text='Past question', days=-5)
        first_choice = past_question.choice_set.first()
        assert first_choice.votes == 0

        url = reverse('polls:vote', args=[past_question.pk])
        response = self.client.post(url, follow=False)
        assert response.status_code == 200
        first_choice.refresh_from_db()
        assert first_choice.votes == 0


class CreateCommentViewTests(TestCase):
    def test_add_comment_anon(self):
        question = create_question(question_text='Past question', days=-5)
        url = reverse('polls:add_comment', args=[question.pk])
        username = 'anon'
        response = self.client.post(
            url, data={'question': question.pk, 'author': username, 'text': 'text'}, follow=True,
        )
        self.assertRedirects(response, reverse('polls:question', args=[question.pk]))
        assert len(Comment.objects.all()) == 1
        assert len(question.comment_set.all()) == 1
        comment = question.comment_set.first()
        assert comment.author == username

    def test_add_comment(self):
        password = 'password'
        user = User.objects.create_user(username='username', password=password)
        self.client.login(username=user.username, password=password)

        question = create_question(question_text='Past question', days=-5)
        url = reverse('polls:add_comment', args=[question.pk])
        response = self.client.post(
            url, data={'question': question.pk, 'author': user.username, 'text': 'text'}, follow=True,
        )
        self.assertRedirects(response, reverse('polls:question', args=[question.pk]))
        assert len(Comment.objects.all()) == 1
        assert len(question.comment_set.all()) == 1
        comment = question.comment_set.first()
        assert comment.author == user.username


class UserViewTests(TestCase):
    def test_user_not_logged_in(self):
        password = 'password'
        user = User.objects.create_user(username='username', password=password)
        url = reverse('polls:user', args=[user.pk])

        response = self.client.get(url, follow=True)
        self.assertRedirects(response, f'{reverse("login")}?next={url}')

    def test_user_logged_in(self):
        password = 'password'
        user = User.objects.create_user(username='username', password=password)
        self.client.login(username=user.username, password=password)

        url = reverse('polls:user', args=[user.pk])
        response = self.client.get(url, follow=False)
        assert response.status_code == 200


class UserListViewTests(TestCase):
    def test_staff_user(self):
        password = 'password'
        admin = User.objects.create_superuser(username='admin', password=password)
        self.client.login(username=admin.username, password=password)

        url = reverse('polls:user_list')
        response = self.client.get(url, follow=False)
        assert response.status_code == 200
        user_list = response.context_data['user_list']
        assert len(user_list) == 1
        assert user_list[0].username == admin.username
