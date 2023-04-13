# makes the cool progress bar in the terminal

def progressBar(progress, total):
    percent = 100 * (progress / total)
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f'\x1b[34;1m|{bar}| {percent:.2f}% \x1b[0m', end="\r")