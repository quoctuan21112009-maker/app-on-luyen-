import json

def convert_assignment_json_to_json(json_data_string: str) -> str:
    """
    Chuyển đổi chuỗi JSON của bài tập thành một chuỗi JSON mới theo cấu trúc yêu cầu
    và áp dụng logic lọc nội dung tùy chọn đã chọn.
    
    Cấu trúc đầu ra yêu cầu:
    {
        'assignId': ...,
        'assignmentContentType': ...,
        'name': ...,
        'data': [
            {
                'stepIndex': ...,
                'content-dataStandard': ...,
                'numberQuestion': ...,
                'typeAnswer': ...,
                'content': [
                    # Logic lọc nội dung:
                    # 1. Nếu typeAnswer == 1 -> Copy toàn bộ giá trị boolean (chuyển sang string) của 'isAnswer' theo thứ tự của 'options'.
                    # 2. Nếu chỉ có MỘT tùy chọn có "isAnswer": true -> Chọn nội dung tùy chọn đó.
                    # 3. Nếu có 0, 2, hoặc nhiều hơn 2 "isAnswer": true, VÀ "rightAnswer": true -> Chọn nội dung các tùy chọn có "userSelected": true.
                    # 4. Các trường hợp còn lại -> Nội dung rỗng ([]).
                ]
            },
            ...
        ]
    }
    """
    try:
        # 1. Tải dữ liệu từ chuỗi JSON đầu vào
        data_json = json.loads(json_data_string)
        detail = data_json.get('data', {}).get('dataDetail', {})

        # Khởi tạo danh sách chứa dữ liệu câu hỏi đã xử lý
        processed_questions = []

        # 2. Lặp qua từng câu hỏi trong danh sách 'data' của 'dataDetail'
        for index, item in enumerate(detail.get('data', [])):
# --- Xử lý list trong dataMaterial.data ---
            q = item.get('dataStandard') 
            
            # Nếu dataStandard không có, kiểm tra dataMaterial và khóa con 'data'
            if q is None:
                data_material = item.get('dataMaterial', {})
                data_content = data_material.get('data') 
                
                # Kiểm tra nếu data_content là một list, lấy phần tử đầu tiên
                if isinstance(data_content, list) and data_content:
                    q = data_content[0]
                # Nếu không phải list hoặc là list rỗng, kiểm tra xem nó có phải là dictionary (Mapping) không
                elif isinstance(data_content, dict):
                    q = data_content
                else:
                    q = {} # Mặc định là dictionary rỗng nếu không tìm thấy dữ liệu hợp lệ
            
            # Nếu vẫn là None (trường hợp dataStandard không có và dataMaterial.data không tồn tại/không hợp lệ), gán q = {}
            if q is None:
                q = {}
            
            # Lấy các giá trị cơ bản của câu hỏi
            question_content = q.get('content', '')
            question_number = q.get('numberQuestion', None)
            is_question_right = q.get('rightAnswer', False)
            type_answer = q.get('typeAnswer', None)
            options = q.get('options', [])
            
            # Tính toán Step Index (Bắt đầu từ 0)
            step_index = index

            # --- 3. ÁP DỤNG LOGIC LỌC NỘI DUNG ĐÃ CẬP NHẬT ---
            
            filtered_contents = []

            # Điều kiện mới (1): Nếu typeAnswer == 1
            if type_answer == 1:
                # Copy toàn bộ giá trị boolean (chuyển sang string) của 'isAnswer'
                # Chuỗi string phải là "true" hoặc "false"
                filtered_contents = [str(opt.get('isAnswer', False)).lower() for opt in options]

            # Áp dụng logic lọc cũ chỉ khi typeAnswer != 1
            else:
                # Tập hợp (set) để lưu trữ nội dung tùy chọn đã lọc (tránh trùng lặp)
                content_set = set()
                
                # Tìm danh sách các tùy chọn có isAnswer = true
                correct_options = [opt for opt in options if opt.get('isAnswer', False)]
                num_correct_options = len(correct_options)

                # Điều kiện cũ (2): Chỉ một đáp án đúng
                if num_correct_options == 1:
                    # Lấy nội dung của đáp án đúng duy nhất đó
                    content = correct_options[0].get('content')
                    if content is not None:
                        content_set.add(content)
                    
                # Điều kiện cũ (3): (0, 2, hoặc >2 đáp án đúng) VÀ câu hỏi được trả lời đúng
                elif is_question_right:
                    # Lấy nội dung của TẤT CẢ các tùy chọn mà người dùng đã chọn
                    for option in options:
                        if option.get('userSelected', False):
                            content = option.get('content')
                            if content is not None:
                                content_set.add(content)
                
                # Điều kiện cũ (4): Các trường hợp còn lại -> Nội dung rỗng (đã được khởi tạo)
                
                # Chuyển set về list cho trường hợp này
                filtered_contents = list(content_set)

            # 4. Tạo dictionary cho câu hỏi đã xử lý
            processed_question = {
                'stepIndex': step_index,
                'content-dataStandard': question_content,
                'numberQuestion': question_number,
                'typeAnswer': type_answer,
                'content': filtered_contents
            }
            processed_questions.append(processed_question)

        # 5. Xây dựng dictionary đầu ra cuối cùng
        output_dict = {
            'assignId': detail.get('id', ''),
            'assignmentContentType': detail.get('assignmentContentType', None),
            'name': detail.get('name', ''),
            'data': processed_questions
        }

        # 6. Chuyển dictionary đầu ra thành chuỗi JSON và trả về
        return json.dumps(output_dict, indent=4, ensure_ascii=False)

    except json.JSONDecodeError as e:
        # In lỗi (có thể loại bỏ)
        print(f"Lỗi giải mã JSON: {e}")
        return json.dumps({}) # Trả về JSON rỗng nếu lỗi
    except Exception as e:
        # In lỗi (có thể loại bỏ)
        print(f"Đã xảy ra lỗi: {e}")
        return json.dumps({}) # Trả về JSON rỗng nếu lỗi

# --- Ví dụ sử dụng để kiểm tra ---
if __name__ == "__main__":
    json_input = """
    {
        "success": true,
        "data": {
            "dataDetail": {
                "id": "69181dc79611cb0b6f95c433",
                "name": "Di truyền liên kết giới tính, liên kết gene và hoán vị gene",
                "assignmentType": 0,
                "assignmentContentType": 0,
                "data": [
                    {
                        "dataStandard": {
                            "content": "Câu 1: Kiểm tra ĐK cũ 1 (Chỉ 1 isAnswer=true)",
                            "options": [
                                {"content": "<p>A: Đáp án đúng duy nhất (isAnswer=true)</p>", "isAnswer": true, "userSelected": false},
                                {"content": "<p>B: Tùy chọn khác</p>", "isAnswer": false, "userSelected": true}
                            ],
                            "rightAnswer": true,
                            "numberQuestion": 13052966,
                            "typeAnswer": 0
                        }
                    },
                    {
                        "dataStandard": {
                            "content": "Câu 2: Kiểm tra ĐK cũ 2 (0 isAnswer=true, rightAnswer=true)",
                            "options": [
                                {"content": "3", "isAnswer": false, "userSelected": true}
                            ],
                            "rightAnswer": true,
                            "numberQuestion": 13052967,
                            "typeAnswer": 5
                        }
                    },
                    {
                        "dataMaterial": {
                            "data": [
                                {
                                    "content": "Câu 3: Kiểm tra ĐK typeAnswer=1 (Copy isAnswer)",
                                    "options": [
                                        {"content": "Đáp án 1", "isAnswer": true, "userSelected": true},
                                        {"content": "Đáp án 2", "isAnswer": false, "userSelected": false},
                                        {"content": "Đáp án 3", "isAnswer": true, "userSelected": true},
                                        {"content": "Đáp án 4", "isAnswer": false, "userSelected": false}
                                    ],
                                    "rightAnswer": true,
                                    "numberQuestion": 13052969,
                                    "typeAnswer": 1
                                }
                            ]
                        }
                    },
                    {
                        "dataStandard": {
                            "content": "Câu 4: Kiểm tra ĐK cũ 3 (Không có isAnswer, rightAnswer=false)",
                            "options": [
                                {"content": "<p>A: Tùy chọn được chọn (userSelected=true)</p>", "isAnswer": false, "userSelected": true},
                                {"content": "<p>B: Tùy chọn không được chọn</p>", "isAnswer": false, "userSelected": false}
                            ],
                            "rightAnswer": false,
                            "numberQuestion": 13052968,
                            "typeAnswer": 2
                        }
                    }
                ]
            }
        },
        "totalRecords": 0, "elapsed": 0.02, "timeServer": 1763293092, "timeResp": "16/11/2025 18:38", "message": "Thành công", "status": 1
    }
    """
    # Thực thi hàm và in kết quả JSON
    result_json = convert_assignment_json_to_json(json_input)

    print("--- Kết Quả JSON Đã Chuyển Đổi ---")
    print(result_json)