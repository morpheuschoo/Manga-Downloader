from mangadex_tv import mangadexTV
from readm_org import readmORG

if __name__ == "__main__":
    print(
        '\x1b[101;1m This programme steals manga from mangadex.tv and readm.org. \x1b[0m\n'
        '\x1b[102;1m Select which website you would like to download your manga from. \x1b[0m\n'
        '\x1b[103;1m readm.org has more reliable scans. \x1b[0m\n\n'
        '\x1b[104;1m Speed of donloader is ~110s per 100 pages. \x1b[0m\n'
    )

    while True:
        print(
            '\x1b[105;1m Select where you would like to download your manga from: \x1b[0m\n'
            '\x1b[106;1m 1: mangadex.tv \x1b[0m\n'
            '\x1b[107;1m 2: readm.org \x1b[0m\n'
        )

        while True:
            try:
                websiteSelection = int(input('Selection: '))
                if websiteSelection in [1, 2]:
                    break
                else:
                    print('Invalid input!')
            except:
                print('Invalid input!')
        
        print()

        if websiteSelection == 1:
            mangadexTV()
            print()
        else:
            readmORG()
            print()