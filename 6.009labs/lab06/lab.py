import sys
from http009 import http_response

import typing
import doctest

sys.setrecursionlimit(10000)

# NO ADDITIONAL IMPORTS!


# custom exception types for lab 6


class HTTPRuntimeError(Exception):
    pass


class HTTPFileNotFoundError(FileNotFoundError):
    pass


# functions for lab 6

def get_file(url):
    """
    This function take in a url, and if there are any redirects returns the correct url. And if there are
    any Errors, raises the error

    Inputs:
        url: A Url representing a file
    Output:
        url: A Url representing a file
    """
    try:
        f = http_response(url) # get the http response 
        status = f.status
        if status == 404: # if 404 raise file not found
            raise HTTPFileNotFoundError
        if status == 500: # if 500 raise file not found
            raise HTTPRuntimeError
        while status in {301, 302, 307}: # while we get a redirect, keep trying to find correct location
            url = f.getheader('location')
            f = http_response(url)
            status = f.status
            # if redirect to a invalid url, raise error
            if status == 404:
                raise HTTPFileNotFoundError
            if status == 500:
                raise HTTPRuntimeError
    except ConnectionError: # if connection error, raise runtime error
        raise HTTPRuntimeError
    return url



# def manifest(url):
    

def download_file(url, chunk_size=8192, cache_dict = None, level = 0):
    """
    Yield the raw data from the given URL, in segments of at most chunk_size
    bytes (except when retrieving cached data as seen in section 2.2.1 of the
    writeup, in which cases longer segments can be yielded).

    If the request results in a redirect, yield bytes from the endpoint of the
    redirect.

    If the given URL represents a manifest, yield bytes from the parts
    represented therein, in the order they are specified.

    Raises an HTTPRuntimeError if the URL can't be reached, or in the case of a
    500 status code.  Raises an HTTPFileNotFoundError in the case of a 404
    status code.
    """
    url = get_file(url) # get url
    if (level == 0): # at the first level of recurion create a new cache dict
        cache_dict = {}
    f = http_response(url)
    if ".parts" == url[-6:] or f.getheader('content-type') == "text/parts-manifest": # if manifest file
        result = 1
        group = b""
        while result != b"": # while we havent reached the end of file
            result = f.readline() # readline
            if result == b"--\n": # if we reach this delimiter, we know we have one group of urls
                group = group.decode('UTF-8').split("\n")
                i = 0
                for url2 in group: # loop through urls and try to yield from them
                    if url2 == '' or url2 == '(*)':
                        continue
                    try:
                        if '(*)' in group: 
                            if url2 in cache_dict: # if it has been cached, dont download just yield from cache
                                yield from cache_dict[url2]
                                i += 1
                                break
                            else: # else yield from download
                                res = tuple(download_file(url2, chunk_size, cache_dict, level +1))
                                cache_dict[url2] = res
                                yield from res
                                i += 1
                        else: # yield from download
                            yield from download_file(url2, chunk_size, cache_dict, level +1)
                            i += 1
                            break
                    # if url raises an error continue onto next one
                    except HTTPFileNotFoundError: 
                        continue
                    except HTTPRuntimeError:
                        continue
                if i == 0: # if no files worked
                    print("No files were valid manifests")
                group = b""
            else:
                group += result
        # this extra loop takes care of the final group in the manifest
        group = group.decode('UTF-8').split("\n")
        i = 0
        for url2 in group:
            if url2 == '' or url2 == '(*)':
                continue
            try:
                if '(*)' in group:
                    if url2 in cache_dict:
                        yield from cache_dict[url2]
                        i += 1
                        break
                    else:
                        res = tuple(download_file(url2, chunk_size, cache_dict, level +1))
                        cache_dict[url2] = res
                        yield from res
                        i += 1
                else:
                    yield from download_file(url2, chunk_size, cache_dict, level +1)
                    i += 1 
                    break
            except HTTPFileNotFoundError: 
                continue
            except HTTPRuntimeError:
                continue
        if i == 0:
            print("None of the urls were valid manifests")
    else:
        # download the file normally
        result = f.read(chunk_size)
        yield result
        size = len(result)
        while size == chunk_size: # if size is different, that means we have read everything in the file and can stop
            result = f.read(chunk_size)
            yield result
            size = len(result)







def files_from_sequence(stream):
    """
    Given a generator from download_file that represents a file sequence, yield
    the files from the sequence in the order they are specified.
    """
    array = bytearray() # create byte array
    for part in stream: # loop through chunks in stream
        array.extend(part)
        if len(array) <= 4: # if length of chunk is less than 4 which gives us file size, continue
            continue
        len_file = array[0]*256**3+array[1]*256**2+array[2]*256+array[3] # get file length
        while len(array) >= len_file + 4: # while there is enough space to get file length and read the file
            yield array[4:len_file + 4] # yield file
            array = array[len_file + 4:] # trim array to new starting point
            try: # get file length
                len_file = array[0]*256**3+array[1]*256**2+array[2]*256+array[3]
            except IndexError: # unless array is not long enough then break out and read more bytes
                break


if __name__ == "__main__":
    url = sys.argv[1]
    filename = sys.argv[2]
    res = http_response(url)
    if "-seq" == url[-4:]:
        i = 1
        file = download_file(url)
        seq = files_from_sequence(file)
        for elem in seq:
            f = open(f'{filename[:-4]}-file{i}{filename[-4:]}', 'wb')
            f.write(elem)
            i += 1
            f.close()
    else:
        with open(filename, "wb") as f:
            file = download_file(url)
            for elem in file:                      
                f.write(elem)
            
        
   
