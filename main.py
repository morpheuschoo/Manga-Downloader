# MANGA DOWNLOADER
# Downloads manga from https://mangadex.tv/
# Search for manga that you want to download from the website
# then input the manga ID into the prompt
# programme downloads every single chapter in the manga

import os
import requests
from PIL import Image
from bs4 import BeautifulSoup
from io import BytesIO

def main():

    mangaID = input('Enter Manga ID: ')

    request = requests.get(f'https://mangadex.tv/manga/{mangaID}')

    if request.status_code != 200:
        print('Manga not found. Please check if Manga ID is valid.')

    requestContent = BeautifulSoup(request.content, 'html.parser')

    mangaTitle = requestContent.findAll('span', class_='mx-1')[0].string

    continueReplyFIRST = input(f'Is the manga that you want to download {mangaTitle}? (Y/N) ')

    if continueReplyFIRST.upper() != 'Y':
        print('Ok program exited.')

    ErrorAllowance = 0

    os.makedirs(mangaTitle)

    for chapterNumber in range(1, 200):
        if ErrorAllowance == 3:
            print('Done downloading!')
            break

        chapter = requests.get(f'https://mangadex.tv/chapter/{mangaID}/chapter-{chapterNumber}')

        if chapter.status_code != 200:
            ErrorAllowance += 1
            print(f'Could not locate chapter {chapterNumber}.')
        else:
            print(f'Currently processing Chapter {chapterNumber} ...')
            
            chapterContent = BeautifulSoup(chapter.content, 'html.parser')

            pageLinks = []

            for row in chapterContent.findAll(class_='noselect nodrag cursor-pointer img-loading'):
                pageLinks.append(row['data-src'])
            
            images = []

            for page in pageLinks:
                response = requests.get(page)

                images.append(Image.open(BytesIO(response.content)))

            images[0].save(f'{mangaTitle}/{mangaTitle} Chapter {chapterNumber}.pdf', 'PDF', save_all=True, resolution=100, append_images=images[1:])

if __name__ == "__main__":
    main()