import requests
from itertools import count
from terminaltables import AsciiTable
from environs import Env


def count_salary(payment_from, payment_to):
    if payment_from is None or not payment_from:
        expected_salary = payment_to*0.8
    elif payment_to is None or not payment_to:
        expected_salary = payment_from*1.2
    else:
        expected_salary = (payment_from+payment_to)/2
    return int(expected_salary)


def predict_rub_salary_for_hh(url_vacancy):
    if url_vacancy['salary'] is None:
        salary = url_vacancy['salary']
        if salary['currency'] == 'RUR':
            return count_salary(salary['from'], salary['to'])
        else:
            return None


def predict_rub_salary_for_superJob(url_vacancy):
    if not url_vacancy['payment_from'] and not url_vacancy['payment_to']:
        return None
    if url_vacancy['currency'] == 'rub':
        return count_salary(url_vacancy['payment_from'], url_vacancy['payment_to'])
    else:
        return None


def get_statistics_of_develop_vacancies_on_hh():
    name_of_programming_languages = ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'C', 'Go']
    develop_vacancy_on_hh = {}
    for language in name_of_programming_languages:
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
        if len(all_salaries):
            average_salary = sum(all_salaries) / len(all_salaries)
        programming_language = {
            'vacancies_found': page_payload['found'],
            'vacancies_processed': len(all_salaries),
            'average_salary': int(average_salary)
        }
        develop_vacancy_on_hh[language] = programming_language
    return develop_vacancy_on_hh


def get_statistics_of_develop_vacancies_on_superJob(superJob_token):
    name_of_programming_languages = ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'C', 'Go']
    develop_vacancy_on_superJob = {}
    for language in name_of_programming_languages:
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
        if len(all_salaries):
            average_salary = sum(all_salaries) / len(all_salaries)
        programming_language = {
            'vacancies_found': page_payload['found'],
            'vacancies_processed': len(all_salaries),
            'average_salary': int(average_salary)
        }
        develop_vacancy_on_superJob[language] = programming_language
    return develop_vacancy_on_superJob


def do_table(develop_vacancy):
    table_data = ()
    salary_table = [('Язык программирования', 'Вакансий найдено', 'Вакансий обработано', 'Средняя зарплата')]
    for programming_language, vacancies in develop_vacancy.items():
        part_of_table = (programming_language, vacancies['vacancies_found'], vacancies['vacancies_processed'], vacancies['average_salary'])
        salary_table.append(part_of_table)
    table_data = tuple(salary_table)
    title = 'Moscow'
    table_instance = AsciiTable(table_data, title)
    table_instance.justify_columns[3] = 'right'
    return table_instance.table


if __name__ == '__main__':
    env = Env()
    env.read_env()
    superJob_token = env.str('SUPER_JOB_TOKEN')
    print(do_table(get_statistics_of_develop_vacancies_on_hh()))
    print(do_table(get_statistics_of_develop_vacancies_on_superJob(superJob_token)))
