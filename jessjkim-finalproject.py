import urllib
from urllib.parse import urlparse
from urllib.request import urlopen
from bs4 import BeautifulSoup
import csv

# Please request a new API key from US Census Bureau if this api key doesn't work and a new key is needed.
apikey = 'fb50683f41424a1ed29617a99f8d18b6cae11db3'

# This function takes in a string and removes any astericks and comma from the string.
def strip_astericks(s):
    return s.replace('*','').replace(',','')

# This function takes in a string and converts the string into a float. If it doesn't work, it returns False.
def convert_float_safe(s):
    try:
        N=int(s)
    except (ValueError, TypeError):
        return (False, "NA")
    return N

def read_trafficking_file(filename): #real_data.csv
    state_agencies = dict()  #key = state_name; value = number of agencies

    with open(filename, 'r', newline='') as input_file:
        state_agencies_reader = csv.DictReader(input_file, delimiter=',', quotechar ='"')

        for row in state_agencies_reader:
            dstate = row['state']
            dagencies = convert_float_safe(strip_astericks(row['agencies']))
            state_agencies[dstate] = dagencies
    return state_agencies

def get_state_fips_code(url):
    response = urllib.request.urlopen(url)
    html_doc = response.read()
    html = html_doc.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    return(soup)

def get_state_abbreviation(url):
    response = urllib.request.urlopen(url)
    html_doc = response.read()
    html = html_doc.decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    row_list = soup.find_all("tr")
    oneList = []
    for state in row_list:
        data = state.find_all("td")
        l=[]
        for d in data:
            str = d.get_text()
            l.append(str)
        oneList.append(l)
    outputDict = {}
    for list in oneList:
        try:
            outputDict[list[0]] = list[1]
        except:
            pass
    return(outputDict)

def make_dict_state_fips_code(soup_name):
    oneDict = {}
    state_rows = soup_name.find_all("tr")
    for row in state_rows:
        tuple = row.find_all("td")
        oneDict[tuple[1].get_text()] = tuple[0].get_text()
    return(oneDict)

def align_fips_code_agencies_data2(d1, d2, d3): #d1 is agencies_dict (state, number of agencies), d2 is dict_state_fips (state, fips code), d3 is state_abbreviation_dict (state, abbr)
    outputDict = {}
    for key in d3: #for every state in state_abbreviation_dict
        if key in d2: #if this state has available fips code
            fips_code = d2[key]
            if key in d1:
                number_agencies = d1[key]
            else:
                number_agencies = 0
            outputDict[fips_code] = (number_agencies, d3[key])
    return(outputDict)

def get_census_data(fips_code):
    base_url = 'http://api.census.gov/data/timeseries/poverty/saipe?get=NAME,SAEPOVRTALL_PT&for=state:'
    back_url = '&time=2014&key='
    total_url = base_url + fips_code + back_url + apikey
    response = urllib.request.urlopen(total_url)
    html_doc = response.read()
    html = html_doc.decode("utf-8")
    t = html.replace("]", "").replace("[", "").replace('"', '')
    f = t.split('\n')
    state_list = f[1].split(",")
    return(state_list) #poverty_rate, fips_code, state_name,


def main():

    # read_trafficking_file function takes in csv file as input.
    # It parses the csv file, cleans up the number of agencies, converts them into float.
    # It returns a dictionary as an output. The output dictionary has state names as its key
    # and the number of participating agencies as its value.
    # Example: {'Idaho': 3.0, 'Maine': 3.0, 'South Dakota': 137.0, ...}
    agencies_dict = read_trafficking_file("human_trafficking_participation_by_state_2015.csv")


    # get_state_fips_code function takes in url, parses the html data of the website using BeautifulSoup,
    # and returns the "soup" data as output of the html file.
    state_fips_code = get_state_fips_code('http://www.columbia.edu/~sue/state-fips.html')

    # make_dict_state_fips_code function takes in the "soup" data from the output of the previous function,
    # finds the table portion within the html document, and finds the records of the state name
    # and the corresponding FIPS code. This function returns a dictionary as an output.
    # The output dictionary has the state name as the key and corresponding FIPS code as the value for each available state.
    # Example: {'Hawaii', '22': 'Louisiana', '11': 'District of Columbia', ... }
    dict_state_fips = make_dict_state_fips_code(state_fips_code)


    # get_state_abbreviation function takes in url as an input, parses the html data of the website using BeautifulSoup,
    # finds the table portion within the html document,
    # and finds the records of the staten names and the corresponding state abbreviation.
    # It returns a dictionary as an output.
    # This output dictionary has state name as its key and state abbrevation as its value for each available state.
    state_abbreviation = get_state_abbreviation('http://www.50states.com/abbreviations.htm')


    # align_fips_code_agencies_data2 function takes in three dictionaries as input:
    # the first dictionary stores state name and number of agencies,
    # the second dictionary stores state name and FIPS code,
    # and the third dictionary stores state name and state abbreviation.
    # It iterates through every state (key) in the state_abbreviation dictionary, finds out whether this state has available FIPS code,
    # and if the state has recorded number of agencies.
    # If the state doesn't have corresponding number of agencies, it will recorded as zero (that it doesn't have any participating agencies).
    # This function returns a dictionary as an output.
    # This dictionary has fips code as the key and a tuple as its value for each matching state.
    # The tuple holds the number of agencies and the state abbreviation.
    # Example: {'15': (3, 'HI'), '29': (637, 'MO'), '32': (45, 'NV'), '05': (296, 'AR'), '56': (57, 'WY'), '48': (1080, 'TX'), ...}
    fips_code_agencies_data = align_fips_code_agencies_data2(agencies_dict,dict_state_fips,state_abbreviation)


    # This code iteratures through every key (FIPS Code) in fips_code_agencies_data dictionary to create a dictionary.
    # For every FIPS code, it goes through the function get_census_data.
    # get_census_data function takes in FIPS code as input and sends an API request to the US Census for each FIPS code.
    # It returns back the state name, the poverty rate in percentage, the year and the corresponding FIPS code.
    # The resulting dictionary holds FIPS code as its key and a list of resulting data (state name, poverty rate, the year)
    # from the data as its value for each matching state.
    # Example: {'20': ['Kansas', '13.5', '2014', '20'], '12': ['Florida', '16.6', '2014', '12'], '28': ['Mississippi', '21.9', '2014', '28'], ...}
    outDict = {}
    for key in fips_code_agencies_data.keys():
         census_data = get_census_data(key)
         outDict[key] = census_data


    # The next block of code combines the data from the two dictionaries above: the outDict and the fips_code_agencies_data
    # to write a new csv file called "poverty_agencies.csv".
    # This csv file holds state name, number of agencies, poverty rate, FIPS code and state abbreviation.
    csv_list = []

    for key in outDict:
         csv_list.append({
             'state_name': outDict[key][0],
             'number_of_agencies': fips_code_agencies_data[key][0],
             'poverty_rate': outDict[key][1],
             'fips_code': key,
             'state_abbr': fips_code_agencies_data[key][1]
         })

    # the resulting csv_list:
    # [{'number_of_agencies': 45, 'state_name': 'Nevada', 'poverty_rate': '15.4', 'fips_code': '32', 'state_abbr': 'NV'},
    # {'number_of_agencies': 1, 'state_name': 'North Carolina', 'poverty_rate': '17.2'

    with open('poverty_agencies.csv', 'w', newline='') as output_file:
         output_writer = csv.DictWriter(output_file,
                                             fieldnames= ['state_name', 'number_of_agencies', 'poverty_rate', 'fips_code', 'state_abbr'],
                                             extrasaction= 'ignore',
                                             delimiter=',', quotechar='"'
                                             )
         output_writer.writeheader()
         for record in csv_list:
             output_writer.writerow(record)


if __name__ == '__main__':
    main()


