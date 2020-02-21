dict = {}
dict["123"] = {"name": "Aaaaa", "sex": "female"}
dict["124"] = {"name": "Bbbbb", "sex": "female"}
dict["125"] = {"name": "Ccccc", "sex": "male"}
dict["126"] = {"name": "Ddddd", "sex": "male"}

print(dict)

dict.pop("123")

for i in dict.items():
    print(i[1]['name'])