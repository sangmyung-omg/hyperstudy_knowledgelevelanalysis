from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Problems, Test_logs
from .form import ProblemForm, Test_oneq_Form
from django.utils import timezone
from .Algorithm_model.Build_Graph_ver3 import Build_Graph
from django.db.models import Count
from django.contrib import messages

# Create your views here.
def welcome(request):
    return render(request, 'hyperstudy/home.html', {})


def problem_list(request):
    problem_list = Problems.objects.order_by('-published_date')
    return render(request, 'hyperstudy/problem_list.html', {'problems': problem_list})


def problem_edit(request, pk):
    problems = get_object_or_404(Problems, pk=pk)
    if request.method == "POST":
        form = ProblemForm(request.POST, instance=problems)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('problem_list')
    else:
        form = ProblemForm(instance=problems)
    return render(request, 'hyperstudy/problem_edit.html', {'form': form})


# 메소드를 나눌 수도 있을 것 같은데 그냥 한 서비스 스트림이라 firsttest에 몰아 넣음.
# 첫 배치고사라고 가정 firsttest
def firsttest(request, num_q=1):
    # GET : 처음 테스트 페이지 부를 때
    if request.method == "GET":
        # 테스트 시작 시 초기 설정
        user = 'Ung'            # 후에 user 아이디 넣어줌
        num_q = 1
        correct_list = []

        # 학생 지식 수준 추적 알고리즘 로딩
        graph = Build_Graph(user)
        first_uk = graph.first_problem()
        # get_object_or_404(Problems, tag_UK=next_uk)           # 해당 data object(row)가 없으면 404 error 띄움
        problems = Problems.objects.filter(tag_UK=first_uk).first()

        # 여기서 correct_list가 리스트 형태로 안 넘어감 ('[]' 형태의 str로 넘어감)
        return render(request, 'hyperstudy/test.html', {'problem': problems, 'num_q': num_q, 'correct_list': correct_list})

    # POST : 첫 테스트 페이지 이후 계속해서 다음 문제 불러올 때
    elif request.method == "POST":
        user = 'Ung'                                                        # 후에 유저 아이디로 치환
        num_q = request.POST.get("num_q")                                   # 문제 번호 (학생에게 보여지는 문제 순서대로 1, 2, 3, ...)
        correct_list = request.POST["correct_list"]                         # Build_Graph에 필요해서 계속 같이 들고 넘김
        response = request.POST.get("answer")                               # 학생이 제출한 답

        # 아무 답도 고르지 않은 채 제출(submit)했을 때 - 경고 메세지
        if response is None:
            messages.error(request, '정답을 체크해주세요!')

            # ** 왜인지는 모르겠으나, html에서 request로 넘어올 때 띄어쓰기 있으면 띄어쓰기 앞의 str만 넘어옴. ex) '식의' of '식의 값'
            # correct_list는 변하지 않았으므로, 현재 UK를 다시 알고리즘으로부터 구함.

            # 학생 지식 수준 추적 알고리즘 로딩
            graph = Build_Graph(user)
            if correct_list != '[]':        # 첫 문제가 아닌 경우 whats_next(correct_list)
                previous_uk = graph.whats_next(list(map(int, correct_list.split(','))))
            else:           # 첫 문제인 경우 first_problem()
                previous_uk = graph.first_problem()
            previous_problem = Problems.objects.filter(tag_UK=previous_uk).first()
            # 같은 페이지로 쏴줌
            return render(request, 'hyperstudy/test.html',
                          {'problem': previous_problem, 'num_q': num_q, 'correct_list': correct_list})

        if correct_list == '[]':                                # 첫 문제일 때
            correct_list = []
        else:
            correct_list = correct_list.split(",")              # "1,1,0,0" (str) 의 형태로 넘어오므로 ["1","1","0","0"]의 형태로 변환
            correct_list = list(map(int, correct_list))         # 각 리스트의 값을 int 형으로 변환

        # DB(문제 리스트)에서 해당 문제의 정답 불러옴 : first() 전에도 row 한 개 (pk로 찾아서)
        problem = Problems.objects.filter(pk=request.POST.get("pk")).first()

        # 학생의 답이 DB(문제 리스트)에 저장된 정답과 같으면 1 / 틀렸으면 0
        if response == str(problem.answer):
            correct_list.append(1)
        elif type(response) == str:
            correct_list.append(0)

        # 정답 여부까지 반영하여 DB에 저장
        test = Test_logs(problem_no=request.POST.get("pk"), tag_UK=request.POST.get("tag_UK"), user=user,
                         response=response, correct=correct_list[-1], published_date=timezone.now())
        test.save()

        # 학생 지식 수준 추적 알고리즘 로딩
        graph = Build_Graph(user)
        # 다음 문제 UK
        next_uk = graph.whats_next(correct_list)

        # 문제 다 풀었으면, correct_list와 wrong_list의 tuple 반환
        if type(next_uk) is tuple:
            return render(request, 'hyperstudy/endtest.html', {'user': user, 'correct_set': ', '.join(next_uk[0]), 'wrong_set': ', '.join(next_uk[1])})

        # 아니면 다음문제
        get_object_or_404(Problems, tag_UK=next_uk)
        next_problem = Problems.objects.filter(tag_UK=next_uk).first()
        # return redirect(reverse('firsttest', kwargs={'num_q': int(request.POST.get("num_q")) + 1, 'next_UK': next_problem}))

        # 다시 correct_list를 str 형태로
        correct_list = ','.join(list(map(str, correct_list)))                       # 7/9 pm 10:14 - correct_list가 render에서 리스트 안보내짐. => join으로 str형태로 보냄.
        return render(request, 'hyperstudy/test.html', {'problem': next_problem, 'num_q': int(num_q) + 1, 'correct_list': correct_list})