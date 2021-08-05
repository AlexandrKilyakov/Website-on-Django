from django.shortcuts import render, redirect
from log_files.models import Gost, Professions, Labor_functions, Tests, Answers
from django.db import connection, transaction

def statistics(requests):
	gost = Gost.objects.order_by("-gost")
	job = Professions.objects.order_by("-name")
	list_glossary = dict()
	test_name = list()
	test_id = list()
	id_test_list = list()
	test_name_list = ""
	test_id_list = ""
	txt_id_answers_list = ""

	if requests.method == "POST":
		Filter_job = requests.POST["job"]
		Filter_gost = requests.POST["gost"]
		Filter_start = requests.POST["afterText"]
		Filter_end = requests.POST["beforeText"]

		lab = Labor_functions.objects.filter(code_profession=Professions.objects.get(name=Filter_job), code_gost=Gost.objects.get(gost=Filter_gost))

		for value in lab:
			test_name.append(str(value.id))

		for value in Answers.objects.all():
			test_id.append(str(value.code_test.id))

		temp_list = list(set(test_name))
		for value in temp_list:
			test_name_list += f"'{value}', "
		

		test = Tests.objects.filter(code_function__in = test_name)
		for value in test:
			id_test_list.append(str(value.id))
			test_id_list += f"{value.id}, "

		answer = Answers.objects.filter(code_test__in = id_test_list, answered__range = [Filter_start, Filter_end])

		for value in answer:
			txt_id_answers_list += f"{value.id}, "

		try:
			filter_lab = Answers.objects.raw(f"SELECT log_files_answers.*, ROUND(cast(SUM(log_files_answers.answer) AS float)/COUNT(log_files_answers.answer), 1) As kol, COUNT(DISTINCT log_files_answers.code_user_id) As kol_users, log_files_tests.type_test, log_files_labor_functions.name AS lab_name, log_files_labor_functions.code_profession_id AS code_profession, log_files_labor_functions.code_gost_id AS code_gost FROM log_files_answers, log_files_labor_functions INNER JOIN log_files_tests ON (log_files_answers.id IN ({txt_id_answers_list[:-2]}) AND log_files_tests.id = log_files_answers.code_test_id AND log_files_labor_functions.id = log_files_tests.code_function_id) GROUP BY log_files_labor_functions.name, log_files_tests.type_test")
			
			for i in range(0, len(list(filter_lab)), 2):
				glossary = {}
				glossary["id"] = filter_lab[i].id
				glossary["kol_users"] = filter_lab[i].kol_users
				glossary["lab_name"] = filter_lab[i].lab_name

				if (str(filter_lab[i].type_test) == "Знания"):
					glossary["know"] = filter_lab[i].kol
					glossary["skill"] = filter_lab[i + 1].kol
				else:
					glossary["skill"] = filter_lab[i].kol
					glossary["know"] = filter_lab[i + 1].kol
				
				glossary["average"] = round((float(glossary["skill"]) + float(glossary["know"])) / 2, 1)
				glossary["code_profession"] = filter_lab[i].code_profession
				glossary["code_gost"] = filter_lab[i].code_gost

				list_glossary[str(i)] = glossary

			return render(requests, 'getstatistics/statistics.html', {"gost": gost, "job": job, "lab": list_glossary, "jobTEST": Filter_job, "gostTEST": Filter_gost, "start":Filter_start , "end": Filter_end, "url_admin": f"{requests.build_absolute_uri()[:-11]}admin", "url_log": f"{requests.build_absolute_uri()[:-11]}log_files", "url_statistic": f"{requests.build_absolute_uri()}"})
		except:
			pass
			
	return render(requests, 'getstatistics/statistics.html', {"gost": gost, "job": job, "url_admin": f"{requests.build_absolute_uri()[:-11]}admin/", "url_log": f"{requests.build_absolute_uri()[:-11]}log_files/", "url_statistic": f"{requests.build_absolute_uri()}"})

def detailed_statistics(requests):
	knows_glossary = dict()
	skills_glossary = dict()
	knows_id_answers_list = ""
	skills_id_answers_list = ""

	if requests.method == "POST":
		code_profession = requests.POST["code_profession"]
		code_gost = requests.POST["code_gost"]
		name = requests.POST["name"]
		skills = requests.POST["skills"]
		know = requests.POST["know"]
		job = requests.POST["jobTEST"]
		gost = requests.POST["gostTEST"]
		start = requests.POST["start"]
		end = requests.POST["end"]

		data_knows = Tests.objects.filter(code_function=Labor_functions.objects.get(name=name, code_profession=Professions.objects.get(id=code_profession), code_gost=Gost.objects.get(id=code_gost)), type_test=know)
		data_skills = Tests.objects.filter(code_function=Labor_functions.objects.get(name=name, code_profession=Professions.objects.get(id=code_profession), code_gost=Gost.objects.get(id=code_gost)), type_test=skills)

		for value in data_knows:
			knows_id_answers_list += f"{value.id}, "

		for value in data_skills:
			skills_id_answers_list += f"{value.id}, "


		filter_knows = Answers.objects.raw(f"SELECT log_files_answers.*, COUNT(log_files_answers.answer) As kol, log_files_tests.name AS test_name, log_files_tests.id AS test_id FROM log_files_answers INNER JOIN log_files_tests ON (log_files_tests.id = log_files_answers.code_test_id AND log_files_tests.id IN ({knows_id_answers_list[:-2]})) GROUP BY log_files_answers.answer, log_files_tests.id")
		filter_skills = Answers.objects.raw(f"SELECT log_files_answers.*, COUNT(log_files_answers.answer) As kol, log_files_tests.name AS test_name, log_files_tests.id AS test_id FROM log_files_answers INNER JOIN log_files_tests ON (log_files_tests.id = log_files_answers.code_test_id AND log_files_tests.id IN ({skills_id_answers_list[:-2]})) GROUP BY log_files_answers.answer, log_files_tests.id")

		for i in range(len(list(filter_knows))):
			
			if(str(filter_knows[i].test_id) in knows_glossary):				
				if(int(filter_knows[i].answer) == 1):
					knows_glossary[str(filter_knows[i].test_id)]["one"] = filter_knows[i].kol
					knows_glossary[str(filter_knows[i].test_id)]["numerator"] += int(filter_knows[i].kol) * 1
					knows_glossary[str(filter_knows[i].test_id)]["denominator"] += int(filter_knows[i].kol)
				if(int(filter_knows[i].answer) == 2):
					knows_glossary[str(filter_knows[i].test_id)]["two"] = filter_knows[i].kol
					knows_glossary[str(filter_knows[i].test_id)]["numerator"] += int(filter_knows[i].kol) * 2
					knows_glossary[str(filter_knows[i].test_id)]["denominator"] += int(filter_knows[i].kol)
				if(int(filter_knows[i].answer) == 3):
					knows_glossary[str(filter_knows[i].test_id)]["three"] = filter_knows[i].kol
					knows_glossary[str(filter_knows[i].test_id)]["numerator"] += int(filter_knows[i].kol) * 3
					knows_glossary[str(filter_knows[i].test_id)]["denominator"] += int(filter_knows[i].kol)
				if(int(filter_knows[i].answer) == 4):
					knows_glossary[str(filter_knows[i].test_id)]["for"] = filter_knows[i].kol
					knows_glossary[str(filter_knows[i].test_id)]["numerator"] += int(filter_knows[i].kol) * 4
					knows_glossary[str(filter_knows[i].test_id)]["denominator"] += int(filter_knows[i].kol)
				if(int(filter_knows[i].answer) == 5):
					knows_glossary[str(filter_knows[i].test_id)]["five"] = filter_knows[i].kol
					knows_glossary[str(filter_knows[i].test_id)]["numerator"] += int(filter_knows[i].kol) * 5
					knows_glossary[str(filter_knows[i].test_id)]["denominator"] += int(filter_knows[i].kol)
				knows_glossary[str(filter_knows[i].test_id)]["average"] = float("{0:.1f}".format(knows_glossary[str(filter_knows[i].test_id)]["numerator"]/knows_glossary[str(filter_knows[i].test_id)]["denominator"]))

			else:
				glossary = {}
				glossary["id"] = filter_knows[i].id
				glossary["name"] = filter_knows[i].test_name
				glossary["one"] = 0
				glossary["two"] = 0
				glossary["three"] = 0
				glossary["for"] = 0
				glossary["five"] = 0
				if(int(filter_knows[i].answer) == 1):
					glossary["one"] = filter_knows[i].kol
					glossary["numerator"] = int(filter_knows[i].kol) * 1
					glossary["denominator"] = int(filter_knows[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_knows[i].kol) * 1 / int(filter_knows[i].kol)))
				if(int(filter_knows[i].answer) == 2):
					glossary["two"] = filter_knows[i].kol
					glossary["numerator"] = int(filter_knows[i].kol) * 2
					glossary["denominator"] = int(filter_knows[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_knows[i].kol) * 2 / int(filter_knows[i].kol)))
				if(int(filter_knows[i].answer) == 3):
					glossary["three"] = filter_knows[i].kol
					glossary["numerator"] = int(filter_knows[i].kol) * 3
					glossary["denominator"] = int(filter_knows[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_knows[i].kol) * 3 / int(filter_knows[i].kol)))
				if(int(filter_knows[i].answer) == 4):
					glossary["for"] = filter_knows[i].kol
					glossary["numerator"] = int(filter_knows[i].kol) * 4
					glossary["denominator"] = int(filter_knows[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_knows[i].kol) * 4 / int(filter_knows[i].kol)))
				if(int(filter_knows[i].answer) == 5):
					glossary["five"] = filter_knows[i].kol
					glossary["numerator"] = int(filter_knows[i].kol) * 5
					glossary["denominator"] = int(filter_knows[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_knows[i].kol) * 5 / int(filter_knows[i].kol)))

				knows_glossary[str(filter_knows[i].test_id)] = glossary

		for i in range(len(list(filter_skills))):
			
			if(str(filter_skills[i].test_id) in skills_glossary):				
				if(int(filter_skills[i].answer) == 1):
					skills_glossary[str(filter_skills[i].test_id)]["one"] = filter_skills[i].kol
					skills_glossary[str(filter_skills[i].test_id)]["numerator"] += int(filter_skills[i].kol) * 1
					skills_glossary[str(filter_skills[i].test_id)]["denominator"] += int(filter_skills[i].kol)
				if(int(filter_skills[i].answer) == 2):
					skills_glossary[str(filter_skills[i].test_id)]["two"] = filter_skills[i].kol
					skills_glossary[str(filter_skills[i].test_id)]["numerator"] += int(filter_skills[i].kol) * 2
					skills_glossary[str(filter_skills[i].test_id)]["denominator"] += int(filter_skills[i].kol)
				if(int(filter_skills[i].answer) == 3):
					skills_glossary[str(filter_skills[i].test_id)]["three"] = filter_skills[i].kol
					skills_glossary[str(filter_skills[i].test_id)]["numerator"] += int(filter_skills[i].kol) * 3
					skills_glossary[str(filter_skills[i].test_id)]["denominator"] += int(filter_skills[i].kol)
				if(int(filter_skills[i].answer) == 4):
					skills_glossary[str(filter_skills[i].test_id)]["for"] = filter_skills[i].kol
					skills_glossary[str(filter_skills[i].test_id)]["numerator"] += int(filter_skills[i].kol) * 4
					skills_glossary[str(filter_skills[i].test_id)]["denominator"] += int(filter_skills[i].kol)
				if(int(filter_skills[i].answer) == 5):
					skills_glossary[str(filter_skills[i].test_id)]["five"] = filter_skills[i].kol
					skills_glossary[str(filter_skills[i].test_id)]["numerator"] += int(filter_skills[i].kol) * 5
					skills_glossary[str(filter_skills[i].test_id)]["denominator"] += int(filter_skills[i].kol)
				skills_glossary[str(filter_skills[i].test_id)]["average"] = float("{0:.1f}".format(skills_glossary[str(filter_skills[i].test_id)]["numerator"]/skills_glossary[str(filter_skills[i].test_id)]["denominator"]))
			else:
				glossary = {}
				glossary["id"] = filter_skills[i].id
				glossary["name"] = filter_skills[i].test_name
				glossary["one"] = 0
				glossary["two"] = 0
				glossary["three"] = 0
				glossary["for"] = 0
				glossary["five"] = 0
				if(int(filter_skills[i].answer) == 1):
					glossary["one"] = filter_skills[i].kol
					glossary["numerator"] = int(filter_skills[i].kol) * 1
					glossary["denominator"] = int(filter_skills[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_skills[i].kol) * 1 / int(filter_skills[i].kol)))
				if(int(filter_skills[i].answer) == 2):
					glossary["two"] = filter_skills[i].kol
					glossary["numerator"] = int(filter_skills[i].kol) * 2
					glossary["denominator"] = int(filter_skills[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_skills[i].kol) * 2 / int(filter_skills[i].kol)))
				if(int(filter_skills[i].answer) == 3):
					glossary["three"] = filter_skills[i].kol
					glossary["numerator"] = int(filter_skills[i].kol) * 3
					glossary["denominator"] = int(filter_skills[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_skills[i].kol) * 3 / int(filter_skills[i].kol)))
				if(int(filter_skills[i].answer) == 4):
					glossary["for"] = filter_skills[i].kol
					glossary["numerator"] = int(filter_skills[i].kol) * 4
					glossary["denominator"] = int(filter_skills[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_skills[i].kol) * 4 / int(filter_skills[i].kol)))
				if(int(filter_skills[i].answer) == 5):
					glossary["five"] = filter_skills[i].kol
					glossary["numerator"] = int(filter_skills[i].kol) * 5
					glossary["denominator"] = int(filter_skills[i].kol)
					glossary["average"] = float("{0:.1f}".format(int(filter_skills[i].kol) * 5 / int(filter_skills[i].kol)))

				skills_glossary[str(filter_skills[i].test_id)] = glossary

		return render(requests, 'getstatistics/detailed_statistics.html', {"data_knows": knows_glossary, "data_skills": skills_glossary, "name": name,"gost": gost, "job": job, "start": start, "end": end})

	return redirect('/statistics/')