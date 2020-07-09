from django.shortcuts import render, get_object_or_404, redirect, reverse
from .models import Problems, Test_logs
from .form import ProblemForm, Test_oneq_Form
from django.utils import timezone

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


def test(request, pk):
    problems = get_object_or_404(Problems, pk=pk)
    if request.method == "POST":
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
