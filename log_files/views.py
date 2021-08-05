from django.shortcuts import render, redirect
from .models import Gost, Professions, Labor_functions, Tests


def download(requests):
	if requests.method == 'POST':
		mainArray = requests.POST["text"].split('0_0')

		jobText = mainArray[0]
		nameArray = mainArray[1].split('|')
		skilsArray = mainArray[2].split('+-+')
		knowArray = mainArray[3].split('+-+')
		gost = mainArray[4]

		try:
			if(not Gost.objects.filter(gost=gost)):
				DB_GOST = Gost(gost=gost)
				DB_GOST.save()

			if(not Professions.objects.filter(name=jobText)):
				DB_JOB = Professions(name=jobText)
				DB_JOB.save()

			if(not bool(Labor_functions.objects.filter(code_profession=Professions.objects.get(name=jobText), code_gost=Gost.objects.get(gost=gost)))):

				for i in range(0, len(nameArray)):
					DB_NAME = Labor_functions(name=nameArray[i], code_profession=Professions.objects.get(name=jobText), code_gost=Gost.objects.get(gost=gost))
					DB_NAME.save()

					tempArray = skilsArray[i].split('|')

					for j in range(0, len(tempArray)):
						DB_SKILS = Tests(name=tempArray[j], type_test="Умения", code_function=Labor_functions.objects.get(name=nameArray[i], code_profession=Professions.objects.get(name=jobText), code_gost=Gost.objects.get(gost=gost)))
						DB_SKILS.save()

					tempArray = knowArray[i].split('|')

					for j in range(0, len(tempArray)):
						DB_KNOW = Tests(name=tempArray[j], type_test="Знания", code_function=Labor_functions.objects.get(name=nameArray[i], code_profession=Professions.objects.get(name=jobText), code_gost=Gost.objects.get(gost=gost)))
						DB_KNOW.save()
		except:
			pass

	gost = Gost.objects.order_by("-gost")
	return render(requests, 'log_files/loading_NameTF.html', {"gost": gost, "url_admin": f"{requests.build_absolute_uri()[:-10]}admin", "url_log": f"{requests.build_absolute_uri()[:-10]}log_files", "url_statistic": f"{requests.build_absolute_uri()[:-10]}statistics"})