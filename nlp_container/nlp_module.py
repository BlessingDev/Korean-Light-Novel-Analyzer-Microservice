import MeCab

import re

dll_path = ""

mecab_special_text_tag = [
    'SSO',
    'SSC',
    'SF',
    'SE',
    'SC',
    'SY'
]

def get_namuwiki_text(sentence) :
    if '#redirect' in sentence :
        return sentence.split()[1]
    else :
        file_p = re.compile('[[][[]파일:.+[]][]]')
        inner_link_p1 = re.compile('[[][[][^파][^일].+[]][]]')
        inner_link_p2 = re.compile('[[][[][^]]+[|][^]]+[]][]]')
        strong_p = re.compile("'''.+'''")
        cancel_p1 = re.compile('~~.+~~')
        cancel_p2 = re.compile('--.+--')
        list_p = re.compile('^[*] ')
        quote_p = re.compile('^>')
        tag_p = re.compile('<.+>')

        table_p = re.compile('[|][|][^|].+[^|][|][|]')
        color_p = re.compile('#\w{6} ')
        html_p1 = re.compile('#!\s+')
        html_p2 = re.compile('\s+=".+"')
        br_p = re.compile('[[]br[]]')

        topic_p = re.compile('=+ .+ =+')
        include_p = re.compile('include[(]틀:')
        root_p = re.compile('/')
        ruby_p = re.compile('[[]ruby[(].+[)][]]')
        title_p = re.compile('[{][{][{].+[}][}][}]')
        title_num_p = re.compile('[{][{][{][+]\d .+[}][}][}]')
        exp_p = re.compile('[[][*].+[]]')


        ### 입구컷 파트 ###

        # 틀 include면 날려버리기
        res = include_p.search(sentence)
        if res is not None :
            return ''

        # 표는 포기할 수 밖에 없었다...
        # 이제 표도 포기하지 않는다!

        ### 내용 삭제 파트 ###
        # 취소선 내용은 삭제한다
        offset = 0
        res = cancel_p1.finditer(sentence)
        for r in res :
            sentence = sentence[:r.start() - offset] + sentence[r.end() - offset:]
            offset += (r.end() - r.start())

        offset = 0
        res = cancel_p2.finditer(sentence)
        for r in res :
            sentence = sentence[:r.start() - offset] + sentence[r.end() - offset:]
            offset += (r.end() - r.start())

        # 파일에 해당하는 부분만 삭제
        offset = 0
        res = file_p.finditer(sentence)
        for r in res :
            sentence = sentence[:r.start() - offset] + sentence[r.end() - offset:]
            offset += (r.end() - r.start())

        # 표에서 삭제할 것 모음
        offset = 0
        res = color_p.finditer(sentence)
        for r in res :
            sentence = sentence[:r.start() - offset] + sentence[r.end() - offset:]
            offset += (r.end() - r.start())

        offset = 0
        res = html_p1.finditer(sentence)
        for r in res :
            sentence = sentence[:r.start() - offset] + sentence[r.end() - offset:]
            offset += (r.end() - r.start())

        offset = 0
        res = html_p2.finditer(sentence)
        for r in res :
            sentence = sentence[:r.start() - offset] + sentence[r.end() - offset:]
            offset += (r.end() - r.start())

        # 리스트는 리스트 표시를 삭제한다
        res = list_p.search(sentence)
        if res is not None :
            sentence = sentence[2:]

        # 인용구 명령어 삭제
        res = quote_p.search(sentence)
        if res is not None :
            sentence = sentence[1:]

        # html 태그는 모두 삭제야!
        res = tag_p.finditer(sentence)
        for r in res :
            sentence = sentence[:r.start()] + sentence[r.end():]

        ### 대입 파트 ###
        # 목차 내용 빼기
        res = topic_p.search(sentence)
        if res is not None :
            sub = sentence[res.start():res.end()]
            eq_num = int(sub.count('=') / 2)
            sub = sub.replace("=" * eq_num, '')

            sentence = sentence[:res.start()] + sub + sentence[res.end():]

        offset = 0
        res = inner_link_p2.finditer(sentence)
        for r in res :
            # 대체말 링크가 있으면 모두 대체말로 바꿔서 넣는다.
            sub = sentence[r.start() - offset:r.end() - offset]
            sub = sub.replace('[[', '').replace(']]', '')
            sub = sub.split('|')[1]

            sentence = sentence[:r.start()- offset] + sub + sentence[r.end() - offset:]
            offset += (r.end() - r.start()) - len(sub)

        # 대체말 링크 다음에는 일반 링크 처리
        offset = 0
        res = inner_link_p1.finditer(sentence)
        for r in res :
            sub = sentence[r.start() - offset:r.end() - offset]
            sub = sub.replace('[[', '').replace(']]', '')

            sentence = sentence[:r.start() - offset] + sub + sentence[r.end() - offset:]
            offset += (r.end() - r.start()) - len(sub)

        offset = 0
        res = strong_p.finditer(sentence)
        for r in res :
            sub = sentence[r.start() - offset:r.end() - offset]
            sub = sub.replace("'''", '')

            sentence = sentence[:r.start() - offset] + sub + sentence[r.end() - offset:]
            offset += (r.end() - r.start()) - len(sub)

        # {{{}}} 묶음 안에 +(숫자)가 붙어 있는 경우의 처리
        offset = 0
        res = title_num_p.finditer(sentence)
        for r in res:
            sub = sentence[r.start() - offset:r.end() - offset]
            sub = sub.replace("{{{", '').replace('}}}', '')
            sub = sub[2:]

            sentence = sentence[:r.start() - offset] + sub + sentence[r.end() - offset:]
            offset += (r.end() - r.start()) - len(sub)


        offset = 0
        res = title_p.finditer(sentence)
        for r in res :
            sub = sentence[r.start() - offset:r.end() - offset]
            sub = sub.replace("{{{", '').replace('}}}', '')

            sentence = sentence[:r.start() - offset] + sub + sentence[r.end() - offset:]
            offset += (r.end() - r.start()) - len(sub)

        # 루비(위첨자) 처리
        res = ruby_p.search(sentence)
        while res is not None :
            offset = 0
            res = ruby_p.finditer(sentence)
            for r in res :
                # 대체말 링크가 있으면 모두 대체말로 바꿔서 넣는다.
                sub = sentence[r.start() - offset:r.end() - offset]
                sub = sub.split(',')[0] + ')]'.join(sub.split(')]')[1:])
                sub = sub[6:]

                sentence = sentence[:r.start()- offset] + sub + sentence[r.end() - offset:]
                offset += (r.end() - r.start()) - len(sub)

            res = ruby_p.search(sentence)

        # 주석 내용 꺼내기
        # 구분할 수 있게 해야한다 (\n)
        offset = 0
        res = exp_p.finditer(sentence)
        for r in res :
            sub = sentence[r.start() - offset:r.end() - offset]
            sub = sub.replace("[*", '\n').replace(']', '')

            sentence = sentence[:r.start() - offset] + sentence[r.end() - offset:] + sub
            offset += (r.end() - r.start()) - len(sub)

        # 표 내용 꺼내기
        offset = 0
        res = table_p.finditer(sentence)
        for r in res:
            sub = sentence[r.start() - offset:r.end() - offset]
            sub = sub.replace("||", '')
            sub = '\n' + sub

            sentence = sentence[:r.start() - offset] + sub + sentence[r.end() - offset:]
            offset += (r.end() - r.start()) - len(sub)

        # / 대체
        sentence = root_p.sub(' ', sentence)

        sentence = br_p.sub('\n', sentence)


        return sentence.strip()

def preprocess_lnv_description(book_list) :
    proccessed_doc = []

    for book in book_list :
        title = book.title
        description = book.description

        sentences = re.compile('[?]|[!]|[.]').split(description)

        # 권수 전처리
        p1 = re.compile('[1-99]권|[1-99]탄')
        # 광고 전처리
        p2 = re.compile('화제작|의 작가|신인상|신작|선사하는|애니메이션|시리즈|수상|'
                       '방영|전작|누계|완결|신인작가|이 라이트노벨이 대단해|인기작|증정|'
                        '코미컬라이즈|한국어판|출간|OSMU')
        match_idx1 = []
        match_idx2 = []
        for i, sentence in enumerate(sentences) :
            sentence = sentence.strip()
            m = p1.search(sentence)
            if m is not None :
                match_idx1.append(i)
            m = p2.search(sentence)
            if m is not None :
                match_idx2.append(i)

        for i in match_idx2 :
            sentences[i] = '광고'

        if len(match_idx1) == 1 :
            sentences[match_idx1[0]] = '권수'
        elif len(match_idx1) > 1 :
            sentences = sentences[match_idx1[len(match_idx1) - 1]:]

        for i in range(sentences.count('')) :
            sentences.remove('')

        proccessed_doc.append(".\n".join(sentences))

    return proccessed_doc

def pos_mecab(sentence) :
    """

    :param sentence:
    :return:
    """
    m = MeCab.Tagger()

    out = m.parse(sentence)

    sentences = out.split('\n')
    sentences = [re.compile('[\t]|,').split(s) for s in sentences]

    return [(s[0], s[1]) for s in sentences if len(s) > 1]

def get_accuracy(title_list, ori_list) :
    """
    책 제목의 유사성을 확인하여 같은 책인지 다른 책인지 0~1 사이의 값으로 반환하는 함수
    두 개의 단어 list를 인자로 받아 책 정확도를 검사
    :param title_list: 비교할 책
    :param ori_list: 기준이 되는 책
    :return: 0.0~1.0 or -1(치명적 차이)
    """
    print(title_list)
    print(ori_list)

    accuracy = 0


    # 두 list의 단어가 비숫한 자리에 있는지
    title_len = len(title_list) - 1
    for i in range(len(ori_list)):
        try:
            if title_list[min(i, title_len)] == ori_list[i] or \
                            title_list[min(i - 1, title_len)] == ori_list[i] or \
                            title_list[min(i + 1, title_len)] == ori_list[i]:
                accuracy += 1
        except:
            print("tried to access index {}".format(i))
            break

    try:
        rate = accuracy / len(ori_list)
    except:
        print('zero devision error')
        return 0.0
    # 측정된 정확도가 일정 이상인데 끝의 숫자가 다르면(즉 같은 시리즈인데 다른 권수일 때)
    if rate >= 0.6 :
        if not ori_list[-1].isdigit() and title_list[-1].isdigit() and \
                        title_list[-1] != '1':
            # 치명적 결과(-1) 반환
            return -1
        elif ori_list[-1].isdigit() and title_list[-1].isdigit() and \
                        title_list[-1] != ori_list[-1]:
            return -1

    # 세트로 발매된 결과를 갖고 왔을 때
    if '세트' in title_list:
        return -1

    len_dif = abs(len(title_list) - len(ori_list))
    #rate -= (len_dif / max(len(title_list), len(ori_list))) * 0.5

    return rate

def search_accsuracy_examine(ori_title, title) :
    """
    검색한 책 제목이 크롤된 책 제목과 맞는지 정확도를 반환하는 함수
    :param book:
    :return:
    """
    # 검색된 제목(book.title)과 크롤된 제목(book.ori_title)을 각각 tagging한다
    ori_nlp = pos_mecab(ori_title)
    title_nlp = pos_mecab(title)

    title_list = list()
    ori_list = list()

    print(ori_nlp, title_nlp)

    # 태그된 데서 단어, 영어, 숫자만 떼어 list화
    punc = False
    for i in title_nlp :
        if i[1] in mecab_special_text_tag :
            if i[0] == '('\
                    or i[0] == '/':
                punc = True
            else :
                punc = False

        if not punc :
            if 'NN' in i[1] or i[1] == 'SN' or i[1] == 'VV'\
                    or i[1] == 'SL':
                if i[0] != '권' :
                    title_list.append(i[0])

    for i in ori_nlp :
        if 'NN' in i[1] or i[1] == 'SN' or i[1] == 'VV'\
                    or i[1] == 'SL':
            ori_list.append(i[0])

    # 정확도을 구한다.
    rate1 = get_accuracy(title_list, ori_list)

    title_list = []

    # 검색된 책제목에서 특수문자('(', '/', '~') 안에 있는 부분만 떼어낸다
    punc = False
    for i in title_nlp:
        if i[1] in mecab_special_text_tag :
            if i[0] == '(' or i[0] == ')'\
                    or i[0] == '/' or i[0] == '~':
                punc = not punc

        if punc :
            if 'NN' in i[1] or i[1] == 'SN' or i[1] == 'VV':
                if i[0] != '권' :
                    title_list.append(i[0])

    #정확도를 구한다
    rate2 = get_accuracy(title_list, ori_list)

    # 크롤된 제목에서 특수문자('(', '/', '~') 안에 있는 부분만 떼어낸다
    ori_list = []
    for i in ori_nlp:
        if i[1] in mecab_special_text_tag :
            if i[0] == '(' or i[0] == ')' \
                    or i[0] == '/' or i[0] == '~':
                punc = not punc

        if punc:
            if 'NN' in i[1] or i[1] == 'SN' or i[1] == 'VV':
                if i[0] != '권':
                    ori_list.append(i[0])

    # 정확도를 구한다
    rate3 = get_accuracy(title_list, ori_list)

    # 치명적인 에러가 없다면 가장 큰 값을 반환한다.
    if rate1 == -1 :
        return 0
    else:
        return max(rate1, rate2, rate3)

def preprocess_title(title) :
    """
    검색된 제목에서 함께 발매된 권수를 때어내기 위한 함수
    ex. 빙결경계의 에덴 1, 2 -> 빙결경계의 에덴 1, 빙결경계의 에덴 2
    :param title: 검색된 책 제목
    :return: titles list
    """
    result = pos_mecab(title)
    title_list = []

    print(result)

    comma_found = False
    first_comma = 0
    # pos 태깅한 어절을 순회
    for i, chunk in enumerate(result):
        # 만약 현재 어절이 ','이고
        # 제목 전체 길이에 비해 0.6보다 뒤에 있다면
        # 분해한다
        if chunk[1] == 'Punctuation' and \
                        chunk[0] == ',' \
                and chunk != result[-1]\
                and ((i + 1) / len(result)) >= 0.6:

            if not comma_found :
                # 만약 현재까지 다른 ,이 없었다면
                first_comma = i - 1
                comma_found = True

                print(first_comma)

                # new_title을 선언하고, 콤마가 등장하기 이전까지의
                # 문자열을 저장한다
                new_title = ""
                for j in range(first_comma):

                    new_title += result[j][0]
                new_title += result[i - 1][0]
                # title_list에 만들어진 제목을 집어넣는다
                title_list.append(new_title)
            else :
                # 다른 ,가 없었다면
                # 처음으로 ,가 등장한 부분까지의 제목을 집어넣고, 권수를 그 뒤에 붙인다.
                new_title = ""
                for j in range(first_comma) :
                    new_title += result[j][0]

                new_title += result[i + 1][0]
                title_list.append(new_title)

        i += 1


    if len(title_list) == 0 :
        # 제대로 분해되지 않았다면 원제목을 다시 넣는다
        title_list.append(title)
    else:

        ori_str = title[:title.find(',')]
        for i in range(len(title_list)) :
            title_list[i] = revive_ori_space(ori_str, title_list[i])

    return title_list

def revive_ori_space(ori_str, new_str) :
    """

    :param ori_str:
    :param new_str:
    :return:
    """
    for i in range(len(ori_str)) :
        if ori_str[i] == ' ' and \
                i < len(new_str) and new_str[i] != ' ':
            new_str = new_str[:i] + ' ' + new_str[i:]

    return new_str

def make_alterative_search_set(title) :
    """
    책을 검색할 때 검색하는 책이 발견되지 않으면 원 제목에서 대체할 검색용 문자열을
    만들어내 반환하는 함수
    :param title:
    :return:
    """
    result = pos_mecab(title)
    title_list = []

    print(result)

    # pos 태깅된 원제목을 순회
    i = 0
    for chunk in result :
        # '시리즈'라는 단어가 나오기 전까지를 대체 검색어로 삼는다
        if chunk[0] == '시리즈' :
            new_title = ""
            for j in range(len(result)) :
                if result[j][0] != '시리즈' :
                    new_title += result[j][0]

            title_list.append(new_title)
        
        # '~'이나 ''' 같은 기호가 나오면 그 다음에 오는 말을 
        # 대체 검색어로 삼는다
        # ex. 쓰르라미 울적에 ~메아카시 편~
        if chunk[1] in mecab_special_text_tag and \
                chunk[0] == '~' or chunk[0] == "'" :
            new_title = ""
            for j in range(i + 1, len(result)) :
                if result[j][1] in mecab_special_text_tag :
                    break
                new_title += result[j][0]
            title_list.append(new_title)

            new_title = ""
            for j in range(i) :
                new_title += result[j][0]
            title_list.append(new_title)

            new_title = ""
            for j in range(len(result)) :
                if j > i - 1 :
                    if result[j][1] not in mecab_special_text_tag :
                        new_title += result[j][0]
                else :
                    new_title += result[j][0]
            title_list.append(new_title)

            break

        i += 1
    
    # 만약 끝 자리가 숫자 1이면 (1권이면)
    # 숫자를 삭제한 것을 대체 검색어로 삼는다
    if result[-1][1] == 'SN' and result[-1][0] == '1' :
        new_title = ""
        for i in range(len(result) - 1) :
            new_title += result[i][0]

        title_list.append(revive_ori_space(title, new_title))

    return title_list
