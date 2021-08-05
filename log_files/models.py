from django.db import models

class Gost(models.Model):
	gost = models.CharField(verbose_name='Профстандарт', max_length = 8)

	def __str__(self):
		return self.gost

	class Meta:
		verbose_name = 'Профстандарт'
		verbose_name_plural = 'Профстандарты'

class Professions(models.Model):
	name = models.CharField(verbose_name='Название', max_length = 225)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Профессия'
		verbose_name_plural = 'Профессии'

class Labor_functions(models.Model):
	name = models.CharField(verbose_name='Название раздела', max_length = 225)
	code_profession = models.ForeignKey('Professions', on_delete=models.CASCADE, verbose_name='Код профессии')
	code_gost =  models.ForeignKey('Gost', on_delete=models.CASCADE, verbose_name='Код профессии')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Раздел'
		verbose_name_plural = 'Разделы'

class Tests(models.Model):
	code_function = models.ForeignKey('Labor_functions', on_delete=models.CASCADE, verbose_name='Код раздела')
	name = models.TextField(verbose_name='Вопрос')
	type_test = models.CharField(verbose_name='Тип вопроса', max_length = 6)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = 'Вопрос'
		verbose_name_plural = 'Вопросы'

class Users(models.Model):
	email = models.CharField(verbose_name='Почта', max_length = 50)

	def __str__(self):
		return self.email

	class Meta:
		verbose_name = 'Испытуемый'
		verbose_name_plural = 'Испытуемые'

class Answers(models.Model):
	code_user = models.ForeignKey('Users', on_delete=models.CASCADE, verbose_name='Код пользователя')
	code_test = models.ForeignKey('Tests', on_delete=models.CASCADE, verbose_name='Код вопроса')
	answer = models.IntegerField(verbose_name='Ответ')
	answered = models.DateField()

	def __str__(self):
		return str(self.answer)

	class Meta:
		verbose_name = 'Ответ'
		verbose_name_plural = 'Ответы'