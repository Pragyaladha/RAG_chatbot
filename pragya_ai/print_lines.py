import pathlib
p=pathlib.Path('chatbot/views.py')
for i,line in enumerate(p.open(),1):
    print(f"{i:3}: {line.rstrip()}")
