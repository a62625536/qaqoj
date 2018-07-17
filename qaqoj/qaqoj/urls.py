from django.contrib import admin
from django.urls import path,include
from account.views import getRegister,getLogin,getLogout
from announcement.views import showAnnouncementList,addAnnouncement
from discussion.views import showDiscussionList,addDiscussion
from problem.views import showProblemsList,addProblem,updateProblem,submitProblem,showRank
from contest.views import showContestList,addContest
from submission.views import showSubmissionList
from hack.views import submitHack,showHackList

urlpatterns = [
    path('superadmin/',admin.site.urls),
    path('register/',getRegister),
    path('login/',getLogin),
    path('logout/',getLogout),
    path('user/',include('account.urls')),
    path('',showAnnouncementList),
    path('addannouncement/',addAnnouncement),
    path('announcement/',include('announcement.urls')),
    path('discussions/',showDiscussionList),
    path('adddiscussion/',addDiscussion),
    path('discussion/',include('discussion.urls')),
    path('problems/',showProblemsList),
    path('problem/',include('problem.urls')),
    path('addproblem/',addProblem),
    path('updateproblem/',updateProblem),
    path('submit/',submitProblem),
    path('contests/',showContestList),
    path('addcontest/',addContest),
    path('contest/',include('contest.urls')),
    path('status/',showSubmissionList),
    path('submission/',include('submission.urls')),
    path('addhack/',submitHack),
    path('hacks/',showHackList),
    path('hack/',include('hack.urls')),
    path('rank/',showRank),
]
