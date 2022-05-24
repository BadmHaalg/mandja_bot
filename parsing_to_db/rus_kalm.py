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

my_dict = docx.Document('rus_kalm.docx')
all_paras = my_dict.paragraphs
for par in all_paras:
    s = par.text.split(' – ')
    try:
        word = s[0]
        article = s[1]
        cur.execute(f"INSERT INTO rus_kalm VALUES ('{word}','{article}');")
        con.commit()
        print(f"{word}, '-', {article}")
    except IndexError:
        pass

print('__succes!!!')
con.close()