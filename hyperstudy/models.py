from django.conf import settings
from django.db import models
from django.utils import timezone

# Create your models here.

class Problems(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # title = models.CharField(max_length=200)
    tag_UK = models.CharField(max_length=200)
    # text = models.TextField()
    problem = models.TextField()
    answer = models.IntegerField()
    created_date = models.DateTimeField(
            default=timezone.now)
    published_date = models.DateTimeField(
            blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.tag_UK


class Test_logs(models.Model):
    # Problems 모델과 DB Relation 표현하면 됨. (problem_no : Foreign key, tag_UK는 JOIN / 아직 몰라서 새로 선언)
    problem_no = models.IntegerField()
    tag_UK = models.CharField(max_length=200)

    # Test_logs의 field 들
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)      # 사용자 Table 만들면 연동
    user = models.CharField(max_length=200)
    response = models.TextField()
    correct = models.IntegerField()
    created_date = models.DateTimeField(
        default=timezone.now)
    published_date = models.DateTimeField(
        blank=True, null=True)