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


def firsttest(request, num_q=1):
    if request.method == "GET":
        graph = Build_Graph('Ung')
        next_UK = ''
        if request.POST.get("next_UK") is None:
            next_UK = graph.first_problem()
        else:
            next_UK = request.POST.get("next_UK")
        get_object_or_404(Problems, tag_UK=next_UK)
        problems = Problems.objects.filter(tag_UK=next_UK).first()
        # print("length of problems :", problems.aggregate(totle_like=Count()))
        num_q = 1
        correct_list = []
        return render(request, 'hyperstudy/test.html', {'problem': problems, 'num_q': num_q, 'correct_list': correct_list})
    elif request.method == "POST":
        user = 'Ung'
        num_q = request.POST.get("num_q")
        correct_list = request.POST["correct_list"]                         # Build_Graph에 필요해서 계속 같이 들고 넘김
        response = request.POST.get("answer")
        print(response)
        if response is None:
            messages.error(request, '정답을 체크해주세요!')
            print(request.POST.get("tag_UK") + '**')
            previous_problem = Problems.objects.filter(tag_UK=request.POST.get("tag_UK")).first()
            # return redirect(reverse('firsttest', kwargs={'problem': previous_problem, 'num_q':num_q, 'correct_list': correct_list}))
            return render(request, 'hyperstudy/test.html',
                          {'problem': previous_problem, 'num_q': num_q, 'correct_list': correct_list})
        print('response:', response)
        if correct_list == '[]':
            correct_list = []
        else:
            correct_list = correct_list.split(",")              # "1,1,0,0" (str) 의 형태로 넘어오므로 ["1","1","0","0"]의 형태로 변환
            correct_list = list(map(int, correct_list))         # 각 리스트의 값을 int 형으로 변환
        graph = Build_Graph(user)
        problem = Problems.objects.filter(pk=request.POST.get("pk")).first()    # 정답 불러옴 : first() 전에도 이미 한개 (pk로 찾기 때문)
        # DB에 저장된 문제 정답과 같으면 1 / 틀렸으면 0
        if response == str(problem.answer):
            correct_list.append(1)
        elif type(response) == str:
            correct_list.append(0)

        # 정답 여부까지 반영하여 DB에 저장장
        test = Test_logs(problem_no=request.POST.get("pk"), tag_UK=request.POST.get("tag_UK"), user=user,
                         response=response, correct=correct_list[-1], published_date=timezone.now())
        test.save()

        # 다음 문제 UK
        next_UK = graph.whats_next(correct_list)

        # 문제 다 풀었으면,
        if type(next_UK) is tuple:
            return render(request, 'hyperstudy/endtest.html', {'user': user, 'correct_set': ', '.join(next_UK[0]), 'wrong_set': ', '.join(next_UK[1])})
        print(next_UK, type(next_UK))

        get_object_or_404(Problems, tag_UK=next_UK)
        next_problem = Problems.objects.filter(tag_UK=next_UK).first()
        # return redirect(reverse('firsttest', kwargs={'num_q': int(request.POST.get("num_q")) + 1, 'next_UK': next_problem}))

        # 다시 correct_list를 보내는 str 형태로
        correct_list = ','.join(list(map(str, correct_list)))                       # 7/9 pm 10:14 - correct_list가 render에서 리스트 안보내짐. => join으로 str형태로 보냄.
        return render(request, 'hyperstudy/test.html', {'problem': next_problem, 'num_q': int(num_q) + 1, 'correct_list': correct_list})


def test(request):
    if request.method == "POST":
        user = 'Ung'            # 나중에 user_id 넣어줌
        graph = Build_Graph(user)
        UK_list = request.POST["tag_UK"]
        if type(UK_list) is str:
            UK_list = [UK_list]
        print(graph.whats_next(UK_list))
        # log = Test_logs.objects.all()
        # form 사용 안함.
        # form = Test_oneq_Form(request.POST, instance=log)
        # if form.is_valid():
        # try:
            # test = form.save(commit=False)
        print(request.POST)
        print("tag_UK :", request.POST.get("tag_UK"))
        print("answer :", request.POST.get("answer"))
        print(request.POST.get("csrfmiddlewaretoken"))
        test = Test_logs(problem_no = pk, tag_UK = request.POST.get("tag_UK"), user=request.POST.get("csrfmiddlewaretoken"), response = request.POST.get("answer"), correct = 1, published_date = timezone.now())
        test.save()
            # test.problem_no = pk
            # test.tag_UK = request.get("tag_UK")
            # test.user = request.user
            # test.response = request.answer
            # test.correct = 1
            # test.published_date = timezone.now()
            # return redirect('/test', {"pk":pk+1})     # 안 됨.
        # except:
        #     test = None
        #     print("Exception~")
        # redirect할 때 parameter 같이 넘기기 (https://bluejake.tistory.com/43)
        return redirect(reverse('test', kwargs={'pk':pk+1}))
    else:
        return render(request, 'hyperstudy/test.html', {'problem': problems})
