from thefuzz import fuzz

kalm_literals = ['ү', 'ә', 'ң', 'ө', 'һ', 'җ']
pairs = {
    'ү': 'у',
    'Ү': 'ү',
    'Ә': 'ә',
    'Ң': 'ң',
    'Ө': 'ө',
    'Һ': 'һ',
    'Җ': 'җ',
    'ә': 'я',
    'ң': 'н',
    'ө': 'о',
    'һ': 'г',
    'җ': 'ж',
}


# similarity уже не очень выборку дает иногда
def standart_fuzzy_wuzzy(query, from_db):
    return fuzz.WRatio(query, from_db)


def custom_fuzzy_wuzzy(similar_list, query_text):
    output_list = []
    for el in similar_list:
        if len(el[0]) == len(query_text):
            for i, lit in enumerate(el[0]):
                if lit in kalm_literals and query_text[i] == pairs[lit]:
                    el[1] += 15
                    if len(el[0]) == 3:
                        el[1] += 15
        if el[1] > 66:
            output_list.append(el)
    out = ''
    a = sorted(output_list, key=lambda x: (x[1], x[2]), reverse=True)
    # принты убрать, обращения писать в логи
    # print(a)
    # print(similar_list)
    for word in a:
        out += word[0] + ', '

    return out[:-2]
