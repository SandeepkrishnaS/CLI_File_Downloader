#!/usr/bin/python3

import click 
import requests 
import threading 
import urllib.parse
  
# The below code is used for each chunk of file handled 
# by each thread for downloading the content from specified  
# location to storage 
def Handler(start, end, url, filename): 
     
    # specify the starting and ending of the file 
    headers = {'Range': 'bytes=%d-%d' % (start, end)} 
  
    # request the specified part and get into variable     
    r = requests.get(url, headers=headers, stream=True) 
  
    # open the file and write the content of the html page  
    # into file. 
    with open(filename, "r+b") as fp: 
      
        fp.seek(start) 
        var = fp.tell() 
        fp.write(r.content) 

@click.command(help="It downloads the specified file with specified name") 
@click.option('--number_of_threads',default=8, help="No. of Threads") 
@click.option('--name',type=click.Path(),help="Name of the file with extension") 
@click.argument('url_of_file',type=click.Path()) 
@click.pass_context 

def download_file(ctx,url_of_file,name,number_of_threads):
    r = requests.head(url_of_file) 
    if name: 
        file_name = name 
    else: 
        file_name = url_of_file.split('/')[-1] 
        file_name = urllib.parse.unquote(file_name)
    try: 
        file_size = int(r.headers['content-length']) 
    except: 
        print("Invalid URL")
        return

    #Creating the temp file
    part = int(file_size / number_of_threads)
    fp = open(file_name, "wb") 
    fp.write(b'\0' * file_size) 
    fp.close() 


    for i in range(number_of_threads): 
        start = part * i 
        end = start + part 
        if i == number_of_threads-1:
            end = file_size
        # create a Thread with start and end locations 
        t = threading.Thread(target=Handler, kwargs={'start': start, 'end': end, 'url': url_of_file, 'filename': file_name}) 
        t.setDaemon(True) 
        t.start() 


    main_thread = threading.current_thread() 
    for t in threading.enumerate(): 
        if t is main_thread: 
            continue
        t.join() 
    print('%s downloaded' % file_name)
  
if __name__ == '__main__': 
    download_file(obj={}) 