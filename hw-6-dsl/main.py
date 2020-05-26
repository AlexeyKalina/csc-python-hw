from preprocessor import Preprocessor
from interpreter import Interpreter

preprocessor = Preprocessor()
interpreter = Interpreter()

program = """
# создание docx из фото дня википедии
[docx] document # есть creation команды для создания сущностей
    title: album.docx # для них можно указывать свойства
    orientation: landscape
    foreach 1..12 # есть циклы по range
        [docx] page # если команда, не из стандартного модуля, его нужно указать перед именем команды
            [docx] p
                text: $month # свойства могут быть вычислимыми, для этого нужно указать $ и calculation команду
                             # для calculation команды можно не указывать последний аргумент - будет подставлен
                             # результат последней calculation команды для текущего блока 
                size: 120
                font: Calibri
                font-style: bold
                align: center
        zfill 2 # calculation команды могут быть и не в свойствах
        join https://ru.wikipedia.org/wiki/Шаблон:Potd/2019-
        [web] load
        foreach [web] xpath //div[contains(@class,'thumbcaption')] # есть циклы по результату calculation команды
            [docx] page
                [docx] p
                    text: $[web] content
                    size: 20
                    font: Calibri
                    align: center
                [web] xpath_one ../a[contains(@class,'image')]/@href
                join https://ru.wikipedia.org
                [web] load
                [web] xpath_one //div[contains(@class,'mw-filepage-resolutioninfo')]/a/@href
                join https:
                [docx] img
                    from_web: true
                    uri: $
                    height: 4.5
                    align: center
                    format: jpeg
"""

clean_program = preprocessor.preprocess(program)
interpreter.interpret(clean_program)
