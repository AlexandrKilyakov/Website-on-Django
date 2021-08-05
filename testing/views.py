from django.shortcuts import render, redirect
from log_files.models import Gost, Professions, Labor_functions, Tests, Answers, Users
from datetime import date
from django.db import connection, transaction


def start(requests):
	gost = Gost.objects.order_by("-gost")
	job = Professions.objects.order_by("-name")
	
	if requests.method == 'POST':
		Filter_job = requests.POST["job"]
		Filter_gost = requests.POST["gost"]

		list_glossary = dict()
		test_name = list()
		test_id = list()
		test_name_list = ""
		test_id_list = ""

		try:
			lab = Labor_functions.objects.filter(code_profession=Professions.objects.get(name=Filter_job), code_gost=Gost.objects.get(gost=Filter_gost))
			
			try:
				element = 0

				list_lab = list(lab)
				
				try:
					passedlist = passed(requests)

					# passedlist.iterator()
					for value in passedlist:
						temp = str(value.code_test.code_function.id)
						temp_test_id = str(value.code_test.id)
						
						test_name.append(temp)
						test_id.append(temp_test_id)

					temp_list = list(set(test_name))
					for value in temp_list:
						test_name_list += f"'{value}', "
					print(temp_list)
					temp_list = list(set(test_id))
					for value in temp_list:
						test_id_list += f"'{value}', "
						
				except Exception as err:
					pass
				
						
				filter_lab = Labor_functions.objects.raw(f"SELECT log_files_labor_functions.name, log_files_labor_functions.id, log_files_tests.type_test FROM log_files_labor_functions INNER JOIN log_files_tests ON (log_files_labor_functions.id IN ({test_name_list[:-2]}) AND log_files_tests.id IN ({test_id_list[:-2]})) GROUP BY log_files_labor_functions.name, log_files_tests.type_test")

				for i in range(len(list(filter_lab))):
					for j in range(len(list(lab))):
						glossary = {}
						if(str(lab[j].id) in list_glossary):
							if (lab[j].id == filter_lab[i].id):
								if (str(filter_lab[i].type_test) == "Знания"):
									list_glossary[str(lab[j].id)]["knows"] = "Знания"

								if (str(filter_lab[i].type_test) == "Умения"):
									list_glossary[str(lab[j].id)]["skills"] = "Умения"
						else:
							
							glossary["id"] = lab[j].id
							glossary["name"] = lab[j].name
							glossary["code_profession"] = lab[j].code_profession.name
							glossary["code_gost"] = lab[j].code_gost.gost

							glossary["knows"] = ""
							glossary["skills"] = ""


							if (lab[j].name == filter_lab[i].name):
								if (str(filter_lab[i].type_test) == "Знания"):
									glossary["knows"] += "Знания"
								if (str(filter_lab[i].type_test) == "Умения"):
									glossary["skills"] += "Умения"
								if(str(lab[j].id) in list_glossary):
									if (str(filter_lab[i].type_test) == "Знания"):
										list_glossary[str(lab[j].id)]["knows"] = "Знания"

									if (str(filter_lab[i].type_test) == "Умения"):
										list_glossary[str(lab[j].id)]["skills"] = "Умения"

							list_glossary[str(lab[j].id)] = glossary

			except Exception as err:
				print(err)
				print("ERROR2")
				pass
			
			if (test_id_list != ""):
				return render(requests, 'testing/main.html', {"gost": gost, "job": job, "glossary": list_glossary, "jobTEST": Filter_job, "gostTEST": Filter_gost})
			else:
				return render(requests, 'testing/main.html', {"gost": gost, "job": job, "lab": lab, "jobTEST": Filter_job, "gostTEST": Filter_gost})
		except Exception as err:
			print(err)
			print("ERROR")

	return render(requests, 'testing/main.html', {"gost": gost, "job": job})

def test(requests):
	gost = Gost.objects.order_by("-gost")
	job = Professions.objects.order_by("-name")

	if requests.method == 'POST':
		code_profession = requests.POST["code_profession"]
		code_gost = requests.POST["code_gost"]
		name = requests.POST["name"]
		skills = requests.POST["skills"]
		know = requests.POST["know"]
		job = requests.POST["jobTEST"]
		gost = requests.POST["gostTEST"]

		data_knows = Tests.objects.filter(code_function=Labor_functions.objects.get(name=name, code_profession=Professions.objects.get(name=code_profession), code_gost=Gost.objects.get(gost=code_gost)), type_test=know)
		data_skills = Tests.objects.filter(code_function=Labor_functions.objects.get(name=name, code_profession=Professions.objects.get(name=code_profession), code_gost=Gost.objects.get(gost=code_gost)), type_test=skills)

		return render(requests, 'testing/test.html', {"data_knows": data_knows, "data_skills": data_skills, "name": name, "gost": gost, "job": job})

	return redirect('/test/')#render(requests, 'testing/error.html', {"url": f"{requests.build_absolute_uri()[:-5]}"})

# ОТВЕТЫ ЗАПИСАТЬ!
def passed(requests):
	try:
		textTEST_knows = requests.POST["textTEST_knows"][:-1]
		textTEST_skills = requests.POST["textTEST_skills"][:-1]
		taxtArray_knows = textTEST_knows.split('|')
		taxtArray_skills = textTEST_skills.split('|')

		for i in range(len(taxtArray_knows)):
			temp = taxtArray_knows[i].split(":")
			if(not bool(Answers.objects.filter(code_user=Users.objects.get(id=int(requests.session.get('id'))), code_test=Tests.objects.get(id=temp[0]), answered=str(date.today())))):
				DB_TEST = Answers(code_user=Users.objects.get(id=int(requests.session.get('id'))), code_test=Tests.objects.get(id=temp[0]), answer=str(temp[1]), answered=str(date.today()))
				DB_TEST.save()


		for i in range(len(taxtArray_skills)):
			temp = taxtArray_skills[i].split(":")
			if(not bool(Answers.objects.filter(code_user=Users.objects.get(id=int(requests.session.get('id'))), code_test=Tests.objects.get(id=temp[0]), answered=str(date.today())))):
				DB_TEST = Answers(code_user=Users.objects.get(id=int(requests.session.get('id'))), code_test=Tests.objects.get(id=temp[0]), answer=str(temp[1]), answered=str(date.today()))
				DB_TEST.save()
	except:
		pass

	return Answers.objects.filter(code_user=Users.objects.get(id=int(requests.session.get('id'))))


def sql_select(sql):
	cursor = connection.cursor()
	cursor.execute(sql)
	results = cursor.fetchall()
	list = []
	i = 0
	for row in results:
		dict = {} 
		field = 0
		while True:
			try:
				dict[cursor.description[field][0]] = str(results[i][field])
				field = field +1
			except IndexError as e:
				break
		i = i + 1
		list.append(dict) 
	return list 

def unique_everseen(seq):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (x in seen or seen_add(x))]





