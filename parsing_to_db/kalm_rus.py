import psycopg2
import docx

db = "tbot"
user = "postgres"

con = psycopg2.connect(
    database=db,
    user=user,
    password="postgres",
    host="127.0.0.1",
    port="5432"
)

print(f'You`re connected to the database "{db}" as user "{user}"')
cur = con.cursor()

my_dict = docx.Document('kalm_rus.docx')
all_paras = my_dict.paragraphs
for par in all_paras:
    s = par.text
    end_of_word = s.find(' ')
    word = s[:end_of_word]
    article = s
    if len(article) <= 1:
        pass
    else:
        print(word, article)
        cur.execute(f"INSERT INTO kalm_rus VALUES ('{word}','{article}');")
        con.commit()

print('__succes!!!')
con.close()
