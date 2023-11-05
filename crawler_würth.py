from urllib import request, error
from bs4 import BeautifulSoup
import json
import matplotlib.pyplot as plt


class GetAllJobs:
    def __init__(self, path, collected_data):
        self.path = path
        self.collected_data = collected_data

    def collect_data(self):
        try:
            html = request.urlopen(self.path)
            xml_syntax = BeautifulSoup(html.read(), "lxml")
            data = xml_syntax.find("tbody")
            data = list(data)
            count = len(data)
            for i, dataset in enumerate(data):
                if i == 0 or i == count-1:
                    continue
                else:
                    dic = {}
                    job_title = dataset.find("td", {"class": {"td-title"}}).text
                    city = dataset.find("td", {"class": {"td-city"}}).text
                    options = dataset.find_all("td", {"class": {"td-options"}})
                    link = dataset.find("td", {"class": {"td-link"}}).find("a")["href"]
                    post = dataset.find("td", {"class": {"td-posted"}}).text
                    dic['job_title'] = job_title
                    dic['city'] = city
                    dic['link'] = link
                    dic['post'] = post
                    if options:
                        keys = ['workspace', 'entry_level', 'working_time', 'start_of_work']
                        for entry in options:
                            dic[keys.pop(0)] = entry.text
                    if dic['job_title'] != '':
                        self.collected_data.append(dic)

        except error.URLError as ERROR:
            print(ERROR)

    def show_current_data(self):
        for dataset in self.collected_data:
            print(dataset)

    def print_current_jobs(self):
        all_job_titles = [dataset['job_title'] for dataset in self.collected_data]
        all_job_titles = list(dict.fromkeys(all_job_titles))
        with open('all_job_titles.txt', 'w') as f:
            for line in all_job_titles:
                f.write(line + '\n')

    def find_job_title(self, job_title):
        data_input = open('mapping_jobs.json', 'r')
        matrix = json.load(data_input)
        data_input.close()
        for department in matrix:
            for job in department['work_titles']:
                if job_title == job:
                    return department['department']

    def draw_charts(self):
        workspaces = [dataset['workspace'] for dataset in self.collected_data]
        workspaces = list(dict.fromkeys(workspaces))
        counter_list = {}
        for dep in workspaces:
            counter_list[dep] = 0
        for dataset in self.collected_data:
            job_title = dataset['job_title']
            rv_dep = self.find_job_title(job_title)
            dataset['department'] = rv_dep
            dep = dataset['workspace']
            counter_list[dep] += 1
        marklist = sorted(counter_list.items(), key=lambda x: x[1])
        sortdict = dict(marklist)
        x = []
        y = []
        for count in sortdict:
            x.append(str(count))
            y.append(sortdict[count])
        x.reverse()
        y.reverse()
        plt.bar(x[0:6], y[0:6], label='Barchart Stellenverteilung', color='blue')
        plt.xlabel('Stelle')
        plt.ylabel('Stellenanzahl')
        plt.title('Stellenverteilung\nin der Firma Würth')
        plt.legend()
        plt.show()


url = 'https://www.wuerth.de/web/de/awkg/karriere/jobs/stellensuche/job-finden.php'
rv = GetAllJobs(url, collected_data=[])
rv.collect_data()
rv.draw_charts()
