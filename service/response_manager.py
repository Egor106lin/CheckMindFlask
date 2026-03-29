from flask import jsonify, Response


class ResponseManager():
    def success_200(self, message: dict = None, data: any = {}) -> Response:
        if message is None:
            message = {
                'ru-RU': 'Успешно',
                'en-EN': 'Successfully'
            }
        return jsonify({
            "status": "success",
            "message": message,
            "data": data
        }), 200

    def error_400(self, message: dict = None) -> Response:
        if message is None:
            message = {
                'ru-RU': 'Что-то пошло не так',
                'en-EN': 'Something went wrong'
            }
        return jsonify({
            "status": "error",
            "message": message
        }), 400

    def error_401(self) -> Response:
        message = {
            "ru-RU": "Требуется повторный вход",
            "en-EN": "Re-entry required"
        }
        return jsonify({
            "status": "error",
            "message": message
        }), 401

    def error_403(self) -> Response:
        message = {
            "ru-RU": "У вас нет прав для совершения этого действия",
            "en-EN": "You do not have the right to perform this action"
        }
        return jsonify({
            "status": "error",
            "message": message
        }), 403

    def error_404(self, message: dict = None) -> Response:
        if message is None:
            message = {
                'ru-RU': 'Необходимые данные не были найдены',
                'en-EN': 'The necessary data was not found'
            }
        return jsonify({
            "status": "error",
            "message": message
        }), 404

    def error_500(self, message: dict = None) -> Response:
        if message is None:
            message = {
                'ru-RU': 'Что-то пошло не так',
                'en-EN': 'Something went wrong'
            }
        return jsonify({
            "status": "error",
            "message": message
        }), 500
    
response_manager = ResponseManager()