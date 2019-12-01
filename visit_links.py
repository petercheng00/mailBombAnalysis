import webbrowser
with open('unsub_links.txt') as f:
    links = f.readlines()
    for i, link in enumerate(links):
        print(f'\r{i}/{len(links)}', end='')
        webbrowser.open_new(link)
    print('')
