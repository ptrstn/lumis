import datetime
import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView

from retriever.lumis import LumiSectionsRetriever
from runreghelper.minmax import get_min_run_number, get_max_run_number


class IndexView(TemplateView):
    template_name = "lumisapp/index.html"

    def get(self, request, *args, **kwargs):
        try:
            run_min = request.GET.get("run_min", None)
            run_max = request.GET.get("run_max", None)

            if run_min and run_max:
                lumis = LumiSectionsRetriever()

                all_lumis = lumis.get_lumis(run_min, run_max)
                good_lumis = lumis.get_lumis(run_min, run_max, good_runs_only=True)
                dcs_ignored_lumis = lumis.get_lumis(run_min, run_max, ignore_dcs=True)

                bad_lumis = {}
                for key, value in all_lumis.items():
                    if key not in good_lumis:
                        bad_lumis[key] = value

                all = json.dumps(all_lumis, sort_keys=True)
                good = json.dumps(good_lumis, sort_keys=True)
                bad = json.dumps(bad_lumis, sort_keys=True)
                dcs_ignored = json.dumps(dcs_ignored_lumis)

                dcs_off_runs = lumis.get_dcs_off_runs(run_min, run_max)

                return render(
                    request,
                    self.template_name,
                    {
                        "all_lumis": all,
                        "good_lumis": good,
                        "bad_lumis": bad,
                        "dcs_ignored": dcs_ignored,
                        "dcs_off": dcs_off_runs,
                    },
                )
            return render(request, self.template_name)
        except:
            return render(request, self.template_name, {"error": True})


def get_min_max_run_number(request):
    current_year = datetime.datetime.now().year
    min_run = get_min_run_number(current_year)
    max_run = get_max_run_number(current_year)
    return JsonResponse({"min": min_run, "max": max_run})
