from flask import Flask, request, jsonify
#from flask_cors import CORS
import json

app = Flask(__name__)

@app.route('/tests/created_test', methods=['POST'])
def test_created_test():
    try:
        data = request.get_json()
        print({type(data)})
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return jsonify({
            "status": "success", 
            "message": "Данные успешно получены",
            "received_data": data
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@app.route('/tests/questions_and_options', methods=['GET'])
def test_questions_and_options():
    try:
        return jsonify({
            "status": "success", 
            "message": "Данные успешно отправлены",
            "data": '{"groupID": "123456789","questionsQuantity": 5,"testName": "Тест для отладки","testDescription": "Тест для проверки работы сайта","questionsAndOptions": [{"question": "1","options": [{"title": "1","correct": true},{"title": "2","correct": false}]},{"question": "2","options": [{"title": "1","correct": true},{"title": "2","correct": false},{"title": "3","correct": true},{"title": "4","correct": false}]},{"question": "3","options": [{"title": "1","correct": true},{"title": "3","correct": false},{"title": "4","correct": false},{"title": "6","correct": false},{"title": "2","correct": true},{"title": "70","correct": false},{"title": "ответ","correct": false}]},{"question": "4","options": [{"title": "ответ 1","correct": true},{"title": "ответ 2","correct": true}]},{"question": "5","options": [{"title": "1","correct": false},{"title": "2","correct": true}]}]}'
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

@app.route('/tests/check_answers', methods=['POST'])
def test_check_answers():
    try:

        return jsonify({
            "status": "success", 
            "message": "Данные успешно получены",
            "data": '{"groupID":"123456789","questionsQuantity":5,"testName":"Тест для отладки","testDescription":"Описание теста для отладки. С помощью него можно сверстать страницу, на которой нужен готовый тест.","result":"4","mistakes":[{"question":"Вопрос 1","correct":true},{"question":"Вопрос 2","correct":true},{"question":"Вопрос 3","correct":false},{"question":"Вопрос 4","correct":true},{"question":"Вопрос 5","correct":false}]}'
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

@app.route('/groups/get_list', methods=['GET'])
def groups_get_list():
    try:

        return jsonify({
            "status": "success", 
            "message": "Данные успешно отправлены",
            "data": '[{"number":1,"owner":"Александр","group_size":15,"name":"Проект","ID":"123456789"},{"number":2,"owner":"Мария","group_size":8,"name":"Группа","ID":"987654321"},{"number":3,"owner":"Иван","group_size":22,"name":"Команда","ID":"456123789"},{"number":4,"owner":"Ольга","group_size":5,"name":"Отдел","ID":"321654987"},{"number":5,"owner":"Дмитрий","group_size":17,"name":"Разработка","ID":"789123456"}]'
        }), 200
        
    except Exception as e:
        print(f"Ошибка при обработке запроса: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    

if __name__ == '__main__':
    app.run(debug=True)
