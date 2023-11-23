import requests
from itertools import count
from terminaltables import AsciiTable
from environs import Env


def predict_rub_salary_for_hh(url_vacancy):
    if url_vacancy['salary']:
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


def find_develop_vacancy_on_hh():
    name_of_programming_languages = ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'C', 'Go']
    develop_vacancy_on_hh = {}
    for language in name_of_programming_languages:
        programming_language = {}
        vacancies = []
        city = '1'
        period = '30'
        for page in count(0):
            payload = {'text': f'программист {language}', 'area': city, 'period': period, 'page': page}
            page_response = requests.get('https://api.hh.ru/vacancies', params=payload)
            page_response.raise_for_status()
            page_payload = page_response.json()
            vacancies.extend(page_payload['items'])
            if page == page_payload['pages'] - 1:
                break
        all_salaries = []
        for vacancy in vacancies:
            salary_for_vacancy = predict_rub_salary_for_hh(vacancy)
            if salary_for_vacancy:
                all_salaries.append(salary_for_vacancy)
        if len(all_salaries) != 0:
            average_salary = sum(all_salaries) / len(all_salaries)
        programming_language['vacancies_found'] = page_payload['found']
        programming_language['vacancies_processed'] = len(all_salaries)
        programming_language['average_salary'] = int(average_salary)
        develop_vacancy_on_hh[language] = programming_language
    return develop_vacancy_on_hh


def find_develop_vacancy_on_superJob():
    name_of_programming_languages = ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'C', 'Go']
    develop_vacancy_on_superJob = {}
    for language in name_of_programming_languages:
        programming_language = {}
        vacancies = []
        city = '4'
        for page in count(0):
            payload = {'t': city, 'keyword': f'программист {language}'}
            headers = {superJob_token}
            page_response = requests.get("https://api.superjob.ru/2.0/vacancies", headers=headers, params=payload)
            page_response.raise_for_status()
            page_payload = page_response.json()
            vacancies.extend(page_payload['objects'])
            if page == page_payload['pages'] - 1:
                break
        all_salaries = []
        for vacancy in vacancies:
            salary_for_vacancy = predict_rub_salary_for_superJob(vacancy)
            if salary_for_vacancy:
                all_salaries.append(salary_for_vacancy)
        if len(all_salaries) != 0:
            average_salary = sum(all_salaries) / len(all_salaries)
        programming_language['vacancies_found'] = page_payload['total']
        programming_language['vacancies_processed'] = len(all_salaries)
        programming_language['average_salary'] = int(average_salary)

        develop_vacancy_on_superJob[language] = programming_language
    return develop_vacancy_on_superJob


def do_table(develop_vacancy):
    table_data = ()
    salary_table = [('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')]
    for programming_language in develop_vacancy.keys():
        part_of_tuple = (programming_language, develop_vacancy[programming_language]['vacancies_found'], develop_vacancy[programming_language]['vacancies_processed'], develop_vacancy[programming_language]['average_salary'])
        salary_table.append(part_of_tuple)
    table_data = tuple(salary_table)
    title = 'Moscow'
    table_instance = AsciiTable(table_data, title)
    table_instance.justify_columns[3] = 'right'
    return table_instance.table


if __name__ == '__main__':
    env = Env()
    env.read_env()
    superJob_token = env.str('SUPER_JOB_TOKEN')
    print(do_table(find_develop_vacancy_on_hh()))
    print(do_table(find_develop_vacancy_on_superJob()))
