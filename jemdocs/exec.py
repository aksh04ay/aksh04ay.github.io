import os

jemdocs=["academics.jemdoc","achievements.jemdoc","contact.jemdoc","courses.jemdoc","extracurrics.jemdoc","index.jemdoc","publications.jemdoc","researchexp.jemdoc","researchintern.jemdoc","selectproject.jemdoc","softwareintern.jemdoc","talks.jemdoc","mmw.jemdoc","ugc.jemdoc"]
for j in jemdocs:
    os.system("python jemdoc.py -c mysite.conf -o ../ "+j)
