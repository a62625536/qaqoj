from django.contrib import admin
from django.urls import path,include
from .views import showContest,updateContest,showContestProblemList,showContestProblem,submitContestProblem,showContestSubmission,showContestStatus,showContestRank

urlpatterns = [
	path('<int:contest_id>',showContest,name="contest"),
	path('<int:contest_id>/update',updateContest),
	path('<int:contest_id>/problems',showContestProblemList),
	path('<int:contest_id>/problem/<int:problem_id>',showContestProblem),
	path('<int:contest_id>/submit',submitContestProblem),
	path('<int:contest_id>/status',showContestStatus),
	path('<int:contest_id>/submission/<int:contestsubmission_id>',showContestSubmission),
	path('<int:contest_id>/rank',showContestRank),
]
