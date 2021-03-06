echo off
chcp 65001 > nul

echo Программа поддерживет следующие параметры:
echo '-c', '--city', default='Санкт-Петербург' - обязательный параметр, имя города либо 'all' - выбор всех города
echo '-y1', '--year1', default=1997 - обязательный параметр, начальный год
echo '-y2', '--year2', default=2021 - обязательный параметр, конечный год
echo '-d', '--download', default=None - параметр, определяющий загрузку. 'simple' - локальная ('mongo' - в БД Mongo, ещё не реализовано)
echo '-a', '--analyze', default=None - параметр, определяющий запуск анализа данных по городу(/ам) на принадлежность к какому-либо климату с выводом в консоль. True или False
echo '-g', '--graph', default=None - параметр, определяющий генерацию графиков. Принимает значения '1', '2', '3', 'all', где: 
echo     1: график самых частовстречающихся значений погодных параметров и их комбинаций 
echo     2: график средних значений температуры за период
echo     3: график(и) температуры день-ночь за период
echo     all: все графики
set /p param=Введите нужные вам параметры:

python "..\app.py" %param%
pause