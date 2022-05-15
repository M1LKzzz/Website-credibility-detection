from django.shortcuts import render, HttpResponse
from trust.models import History
from trust.detect_func import wjc
import trust.detect as detect


test_url = ''
trust_value = 0
contained_wjc = ''
have_dangerous_file = False


def suffix_detection():
    global test_url
    if test_url[-3::1] == 'gov' or test_url[-3::1] == 'edu':
        return 1
    else:
        return 0


def index(request: HttpResponse):
    if request.method == 'POST':
        global test_url, trust_value, contained_wjc, have_dangerous_file
        test_url = request.POST.get("url", None)
        wjc.wjc_detect(test_url)
        with open('OK.csv', 'r') as fp:
            lines = fp.readlines()
            contained_wjc = lines[0]
            fp.close()
        with open("OK.csv", 'r+') as f:
            f.truncate(0)

        have_dangerous_file = detect.file_detect(test_url)
        trust_value = suffix_detection()
        history = History(url=test_url, trust_value=trust_value, have_dangerous_file=have_dangerous_file)
        history.save()
    return render(request,
                  'trust/index.html',
                  {"test_url": test_url, "trust_value": trust_value, "contained_wjc": contained_wjc,  "have_dangerous_file": have_dangerous_file}
                  )


