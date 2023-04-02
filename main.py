# MANGA DOWNLOADER
# Downloads manga from https://mangadex.tv/
# Search for manga that you want to download from the website
# programme downloads every single chapter or selected chapters in the manga

import os
import sys
import re
import requests
from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO

application_path = os.path.dirname(sys.executable)

def main():

    # information
    print(
        'This programme steals manga from https://mangadex.tv/.\n'
        'Search for manga here and download it to your computer.\n'
    )

    # takes in user search
    search = input('Search on MangaDex: ')

    search = re.sub(' ', '+', search)

    searchWebpage = requests.get(f'https://mangadex.tv/search?type=titles&title={search}&submit=')

    if searchWebpage.status_code != 200:
        print('Invalid search!')
        return 1

    searchWebpageContent = BeautifulSoup(searchWebpage.content, 'html.parser')

    titleLink = [[row['title'], row['href']] for row in searchWebpageContent.findAll(class_='ml-1 manga_title text-truncate', limit=5)]

    if len(titleLink) == 0:
        print('No manga found.')
        return 1

    print()
    print('Select an option:')
    for index, value in enumerate(titleLink):
        print(f'{index + 1}: {value[0]}')

    print()
    mangaSelection = input('Selection: ')

    try:
        mangaSelection = int(mangaSelection)
    except:
        print('Invalid selection!')
        return 1

    if mangaSelection < 1 or mangaSelection > 5:
        print('Invalid selection!')
        return 1

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
        chapterTitles.append(row.string)
        chapterLinks.append(row['href'])

    print()
    print(f'I have found these chapters from {mangaTitle}:')
    for index, title in enumerate(chapterTitles):
        print(f'{index + 1}: {title}')

    print(
        '\n'
        'Tell me the chapters you would like to download (by index):\n'
        'ALL CHAPTERS: ALL\n'
        'RANGE: 1-5, 7, 9, 12-13, ...\n'
        'NONE: NONE'
    )

    print()
    chapterSelection = input('Selection: ')

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
    
    # chapterSelectionPROCESSED contains all the indexes of chapters being processed
    chapterSelectionPROCESSED = set()

    if chapterSelection == 'none':
        print('Ok program exited')
        return 1
    elif chapterSelection == 'all':
        chapterSelectionPROCESSED = {x for x in range(len(chapterTitles))}
    else:
        for value in chapterSelection:
            if type(value) == list:
                for x in range(value[0], value[1] + 1):
                    chapterSelectionPROCESSED.add(x - 1)
            else:
                chapterSelectionPROCESSED.add(value - 1)

    # ensures that special symbols removed
    mangaTitle = re.sub('<|>|:|"|/|\\|\?|\*', ' ', mangaTitle)

    # make a folder with the manga title as its name
    os.makedirs(f'{application_path}/{mangaTitle}')

    print()

    # iterrates though selection and downloads each chapter
    for x in chapterSelectionPROCESSED:

        # access individual chapters of the manga
        chapter = requests.get(f'https://mangadex.tv{chapterLinks[x]}')

        if chapter.status_code != 200:
            print(f'Could not locate {chapterTitles[x]}.')
        else:
            print(f'Currently processing {chapterTitles[x]}...')
            
            chapterContent = BeautifulSoup(chapter.content, 'html.parser')

            pageLinks = []

            # obtain each image link in each chapter
            for row in chapterContent.findAll(class_='noselect nodrag cursor-pointer img-loading'):
                pageLinks.append(row['data-src'])
            
            images = []

            # download images from image links
            for page in pageLinks:
                response = requests.get(page)

                images.append(Image.open(BytesIO(response.content)))
            
            chapterTitle = re.sub('<|>|:|"|/|\\|\?|\*', ' ', chapterTitles[x])

            # save each chapter as a pdf file
            images[0].save(f'{application_path}/{mangaTitle}/{chapterTitle}.pdf', 'PDF', save_all=True, resolution=100, append_images=images[1:])

            print('Done downloading!')

            return 0

if __name__ == "__main__":
    main()