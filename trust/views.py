from charset_normalizer import detect
from django.shortcuts import render, HttpResponse
from sqlalchemy import null
from trust.models import History
from trust.wjc_detection import wjc
from trust.phishing_detection import phishing
from trust.file_detect import detect
import os
import re


test_url = ''
trust_value = 0
contained_wjc = ''
phishing_website = False
have_dangerous_file = False
url_flag = True





def index(request: HttpResponse):
    if request.method == 'POST':
        global test_url, trust_value, contained_wjc, phishing_website, have_dangerous_file, url_flag
        test_url = request.POST.get("url", None)
        pattern = re.compile(r'(https?)?:?//[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]')
        if not pattern.search(test_url):
            url_flag = False
        else:
            url_flag = True
            wjc.wjc_detect(test_url)
            with open('OK.csv', 'r') as fp:
                lines = fp.readlines()
                if not os.path.getsize('OK.csv'):
                    contained_wjc = ''
                else:
                    contained_wjc = lines[0]
                fp.close()
            with open("OK.csv", 'r+') as f:
                f.truncate(0)

            have_dangerous_file = detect.file_detect(test_url)
            phishing_website = phishing.phishing_detect(test_url)
            history = History(url=test_url, trust_value=trust_value)
            history.save()
            if have_dangerous_file or phishing_website or contained_wjc:
                trust_value = 0
            else:
                trust_value = 1
    return render(request,
                  'trust/index.html',
                  {"test_url": test_url, "url_flag": url_flag, "trust_value": trust_value, "contained_wjc": contained_wjc, "phishing_website": phishing_website, "have_dangerous_file":have_dangerous_file}
                  )


