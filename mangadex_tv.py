# Downloads manga from https://mangadex.tv/
import os
import sys
import re
import requests
from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO

from progress_bar import progressBar

application_path = os.path.dirname(sys.executable)

def mangadexTV():
    while True:

        # takes in user search
        search = input('Search on mangadex: ')

        search = re.sub(' ', '+', search)

        searchWebpage = requests.get(f'https://mangadex.tv/search?type=titles&title={search}&submit=')

        if searchWebpage.status_code != 200:
            print('Webpage not found!')
        else:
            searchWebpageContent = BeautifulSoup(searchWebpage.content, 'html.parser')

            titleLink = [[row['title'], row['href']] for row in searchWebpageContent.findAll(class_='ml-1 manga_title text-truncate', limit=5)]

            if len(titleLink) == 0:
                print('No manga found.')
            else:
                break

    print('\nSelect an option:')
    for index, value in enumerate(titleLink):
        print(f'{index + 1}: {value[0]}')

    mangaSelection = input('\nSelection: ')

    while True:
        try:
            # ensure that integer is inputted
            mangaSelection = int(mangaSelection)

            # ensure selection is within range
            if mangaSelection < 1 or mangaSelection > len(titleLink):
                print('Invalid input!')
                mangaSelection = input('Please retype selection: ')
            else:
                break
        except:
            print('Invalid input!')
            mangaSelection = input('Please retype selection: ')

    # access main page of manga
    request = requests.get(f'https://mangadex.tv{titleLink[int(mangaSelection) - 1][1]}')

    # check if manga ID is valid
    if request.status_code != 200:
        print('Manga not found. Please check if Manga ID is valid.')
        return 1

    requestContent = BeautifulSoup(request.content, 'html.parser')

    mangaTitle = requestContent.findAll('span', class_='mx-1')[0].string

    chapterTitles = []
    chapterLinks = []

    for row in reversed(requestContent.findAll('a', class_='text-truncate')):
        chapterTitles.append(row.string.strip())
        chapterLinks.append(row['href'])

    print(f'\nI have found these chapters from {mangaTitle}:')
    for index, title in enumerate(chapterTitles):
        print(f'{index + 1}: {title}')

    print(
        '\n'
        'Tell me the chapters you would like to download (by index):\n'
        'ALL CHAPTERS: ALL\n'
        'RANGE: 1-5, 7, 9, 12-13, ...\n'
        'NONE: NONE'
    )

    chapterSelection = input('\nSelection: ')

    while True:
        if not ',' in chapterSelection:
            chapterSelection = chapterSelection.lower()

        if chapterSelection == 'all' or chapterSelection == 'none':
            break

        chapterSelection = chapterSelection.replace(' ', '')

        errorValues = []

        chapterSelection = chapterSelection.split(',')

        chapterSelection = [value.split('-') if '-' in value else value for value in chapterSelection]

        for index, value in enumerate(chapterSelection):
            if type(value) == list:
                
                # ensure no inputs are like 1-4-7
                if len(value) != 2:
                    errorValues.append('-'.join(value))
                
                # ensure all inputs are integers
                try:
                    chapterSelection[index] = [int(x) for x in value]

                    # ensure no inputs are like 20-11
                    if chapterSelection[index][0] > chapterSelection[index][1]:
                        errorValues.append('-'.join(value))

                    # ensure no input is smaller than 1 or out of range
                    if chapterSelection[index][0] < 1 or chapterSelection[index][1] > len(chapterTitles):
                        errorValues.append('-'.join(value))
                except:
                    errorValues.append('-'.join(value))
                
            else:
                # ensure all inputs are integers
                try:
                    chapterSelection[index] = int(value)

                    # ensure no input is smaller than 1 or out of range
                    if chapterSelection[index] < 1 or chapterSelection[index] > len(chapterTitles):
                        errorValues.append(value)
                except:
                    errorValues.append(value)

        if len(errorValues) != 0:
            print('Invalid input for the following: ' + ', '.join(errorValues) + '.')
            chapterSelection = input(f'Please retype selection: ')
        else:
            break
    
    # chapterSelectionProcessed contains all the indexes of chapters being processed
    chapterSelectionProcessed = set()

    if chapterSelection == 'none':
        print('Ok program exited')
        return 1
    elif chapterSelection == 'all':
        chapterSelectionProcessed = {x for x in range(len(chapterTitles))}
    else:
        for value in chapterSelection:
            if type(value) == list:
                for x in range(value[0], value[1] + 1):
                    chapterSelectionProcessed.add(x - 1)
            else:
                chapterSelectionProcessed.add(value - 1)

    print()

    # ensures that special symbols removed
    mangaTitle = re.sub('<|>|:|"|/|\\\|\?|\*', ' ', mangaTitle)

    # make a folder with the manga title as its name
    # if folder present inform user that files will be stored there
    if os.path.isdir(f'{application_path}/{mangaTitle}'):
        print(f'Folder name - {mangaTitle} - is present, storing files there.')
    else:
        os.makedirs(f'{application_path}/{mangaTitle}')

    chaptersDownloaded = 0

    # iterrates though selection and downloads each chapter
    for x in sorted(chapterSelectionProcessed):

        # access individual chapters of the manga
        chapter = requests.get(f'https://mangadex.tv{chapterLinks[x]}')

        percentage = chaptersDownloaded / len(chapterSelectionProcessed) * 100

        if chapter.status_code != 200:
            print(f'\x1b[41;1m <{percentage:.2f}%> Could not locate {chapterTitles[x]}. \x1b[0m')
        else:
            print(f'\x1b[42;1m <{percentage:.2f}%> Currently downloading {chapterTitles[x]}... \x1b[0m')
            
            chapterContent = BeautifulSoup(chapter.content, 'html.parser')

            pageLinks = []

            # obtain each image link in each chapter
            for row in chapterContent.findAll(class_='noselect nodrag cursor-pointer img-loading'):
                pageLinks.append(row['data-src'])

            try:
                images = []

                pageNumber = 0

                print('\x1b[?25l', end="")

                progressBar(pageNumber, len(pageLinks))

                # download images from image links
                for page in pageLinks:
                    response = requests.get(page)

                    images.append(Image.open(BytesIO(response.content)))

                    pageNumber += 1
                    progressBar(pageNumber, len(pageLinks))
                
                chapterTitle = re.sub('<|>|:|"|/|\\\|\?|\*', ' ', chapterTitles[x])

                # save each chapter as a pdf file
                images[0].save(f'{application_path}/{mangaTitle}/({x + 1}) {chapterTitle}.pdf', 'PDF', save_all=True, resolution=100, append_images=images[1:])

                print('\x1b[?25h\x1b[1F\x1b[0J', end="")
                print(f'\x1b[42;1m <{percentage}%> Downloaded {chapterTitles[x]}. \x1b[0m')
            except:
                print('\x1b[1F\x1b[0J', end="")
                print(f'\x1b[41;1m Images for {chapterTitles[x]} could not be found. \x1b[0m')
                print('\x1b[41;1m Website could have uploaded corrupted files. \x1b[0m')
            
        chaptersDownloaded += 1

    print('\x1b[43;1m <100%> Done downloading! \x1b[0m')

    return 0