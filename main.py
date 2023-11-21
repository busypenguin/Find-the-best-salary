import requests
from itertools import count
from terminaltables import AsciiTable


def predict_rub_salary_for_hh(url_vacancy):
    if url_vacancy['salary'] is not None:
        salary = url_vacancy['salary']
        if salary['currency'] == 'RUR':
            if salary['from'] is None:
                expected_salary = salary['to']*0.8
            elif salary['to'] is None:
                expected_salary = salary['from']*1.2
            else:
                expected_salary = (salary['from']+salary['to'])/2
            return int(expected_salary)
        else:
            return None


def predict_rub_salary_for_superJob(url_vacancy):
    if url_vacancy['payment_from'] == 0 and url_vacancy['payment_to'] == 0:
        return None
    if url_vacancy['currency'] == 'rub':
        if url_vacancy['payment_from'] == 0:
            expected_salary = url_vacancy['payment_to']*0.8
        elif url_vacancy['payment_to'] == 0:
            expected_salary = url_vacancy['payment_from']*1.2
        else:
            expected_salary = (url_vacancy['payment_from']+url_vacancy['payment_to'])/2
        return int(expected_salary)
    else:
        return None


def find_develop_dict_for_hh():
    developers = ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'C', 'Go']
    develop_dict_for_hh = {}
    for developer in developers:
        programming_language = {}
        vacancies = []
        for page in count(0):
            payload = {'text': f'программист {developer}', 'area': '1', 'period': '30', 'page': page}
            page_response = requests.get('https://api.hh.ru/vacancies', params=payload)
            page_response.raise_for_status()
            page_payload = page_response.json()
            for page_vacancy in page_payload['items']:
                vacancies.append(page_vacancy)
            if page == page_payload['pages'] - 1:
                break
        i = 0
        all_salary = []
        sum_of_salary = 0
        for vacancy in vacancies:
            if predict_rub_salary_for_hh(vacancy) is not None:
                all_salary.append(predict_rub_salary_for_hh(vacancy))
                i += 1
                sum_of_salary = sum_of_salary + predict_rub_salary_for_hh(vacancy)
        average_salary = sum_of_salary / i
        programming_language['vacancies_found'] = len(vacancies)
        programming_language['vacancies_processed'] = i
        programming_language['average_salary'] = int(average_salary)

        develop_dict_for_hh[developer] = programming_language
    return develop_dict_for_hh


def find_develop_dict_for_superJob():
    developers = ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'C', 'Go']
    develop_dict_for_superJob = {}
    for developer in developers:
        programming_language = {}
        vacancies = []
        for page in count(0):
            payload = {'t': '4', 'keyword': f'программист {developer}'}
            headers = {
            'X-Api-App-Id': 'v3.r.137964674.8f78016b701cf978a5ef350fe7ad05cd1ff5d324.d3ee76c54c90e6cda16f6b0546c58c1333a2306c'
            }
            page_response = requests.get("https://api.superjob.ru/2.0/vacancies", headers=headers, params=payload)
            page_response.raise_for_status()
            page_payload = page_response.json()
            for page_vacancy in page_payload['objects']:
                vacancies.append(page_vacancy)
            if page == page_payload['pages'] - 1:
                break
        i = 0
        all_salary = []
        sum_of_salary = 0
        for vacancy in vacancies:
            if predict_rub_salary_for_superJob(vacancy) is not None:
                all_salary.append(predict_rub_salary_for_superJob(vacancy))
                i += 1
                sum_of_salary = sum_of_salary + predict_rub_salary_for_superJob(vacancy)
        average_salary = sum_of_salary / i
        programming_language['vacancies_found'] = len(vacancies)
        programming_language['vacancies_processed'] = i
        programming_language['average_salary'] = int(average_salary)

        develop_dict_for_superJob[developer] = programming_language
    return develop_dict_for_superJob


def do_table_for_superJob(develop_dict_for_superJob):
    TABLE_DATA = ()
    list_for_table = [('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')]
    for key in develop_dict_for_superJob.keys():
        part_of_tuple = (key, develop_dict_for_superJob[key]['vacancies_found'], develop_dict_for_superJob[key]['vacancies_processed'], develop_dict_for_superJob[key]['average_salary'])
        list_for_table.append(part_of_tuple)
    TABLE_DATA = tuple(list_for_table)
    title = 'SuperJob Moscow'
    table_instance = AsciiTable(TABLE_DATA, title)
    table_instance.justify_columns[3] = 'right'
    print(table_instance.table)
    print()


def do_table_for_hh(develop_dict_for_hh):
    TABLE_DATA = ()
    list_for_table = [('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')]
    for key in develop_dict_for_hh.keys():
        part_of_tuple = (key, develop_dict_for_hh[key]['vacancies_found'], develop_dict_for_hh[key]['vacancies_processed'], develop_dict_for_hh[key]['average_salary'])
        list_for_table.append(part_of_tuple)
    TABLE_DATA = tuple(list_for_table)
    print(TABLE_DATA)
    title = 'HeadHunter Moscow'
    table_instance = AsciiTable(TABLE_DATA, title)
    table_instance.justify_columns[3] = 'right'
    print(table_instance.table)
    print()


do_table_for_hh(find_develop_dict_for_hh())
do_table_for_superJob(find_develop_dict_for_superJob())
