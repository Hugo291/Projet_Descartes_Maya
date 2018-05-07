from app.models.DataBase import PdfFile , db

#select raw query
result = db.session.execute("SELECT * FROM user")
for row in result:
    for element in row:
        pass    #print(element)

liste = PdfFile.query.filter(PdfFile.id ==1000).all()
element = PdfFile.query.filter(PdfFile.id ==1000).first()

print('liste -> '+str(liste))
print('element -> '+str(element))